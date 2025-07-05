"""album_avg_daily_plays.py

Graphs the top N albums based on average plays per day since the album
was added.
"""

from typing import Any, Dict

import matplotlib.pyplot as plt
import pandas as pd

from src.analysis._utils_ import (
    ensure_columns,
    get_today_matching_tz,
    save_plot,
    trim_label,
)


def run(tracks_df: pd.DataFrame, params: Dict[str, Any], output_path: str) -> str:
    """This run() function is executed by the analysis engine."""

    ensure_columns(tracks_df, ["Play Count", "Date Added", "Album"])

    df = tracks_df.dropna(subset=["Play Count", "Date Added", "Album"]).copy()

    # Convert Play Count to numeric, fill missing values with 0
    df["Play Count"] = (
        pd.to_numeric(df["Play Count"], errors="coerce").fillna(0).astype(int)
    )
    df["Date Added"] = pd.to_datetime(df["Date Added"], errors="coerce")
    df = df.dropna(subset=["Date Added"])

    # For each album, get the sum of play counts and the earliest date added
    album_stats = (
        df.groupby("Album")
        .agg(
            Total_Play_Count=("Play Count", "sum"),
            Earliest_Date_Added=("Date Added", "min"),
        )
        .reset_index()
    )

    today = get_today_matching_tz(df["Date Added"])

    album_stats["Days In Library"] = (
        today - album_stats["Earliest_Date_Added"].dt.floor("D")
    ).dt.days.clip(lower=1)
    album_stats["Avg Daily Plays"] = (
        album_stats["Total_Play_Count"] / album_stats["Days In Library"]
    )

    # Get top N albums by average daily plays
    window = album_stats.sort_values("Avg Daily Plays", ascending=False).head(
        params["top"]
    )

    # Trim long names
    window["Album (Trimmed)"] = window["Album"].apply(trim_label)

    # Set figure height dynamically based on number of rows
    plt.figure(figsize=(6, max(2, len(window) * 0.35)))

    # Plot the results
    window[::-1].plot(
        kind="barh",
        x="Album (Trimmed)",
        y="Avg Daily Plays",
        color=plt.get_cmap("tab10").colors,
        edgecolor="black",
        legend=False,
        ax=plt.gca(),
    )
    plt.xlabel("Average Daily Plays")
    title = f"Top {params['top']} Albums by Average Daily Plays"
    save_plot(title, output_path, ext="png", dpi=300)

    return f"{output_path}.png"
