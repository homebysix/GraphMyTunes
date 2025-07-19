"""album_avg_daily_plays.py

Graphs the top N albums based on average plays per day since the album
was added.
"""

import logging
import os
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd

from src.analysis._utils_ import (
    create_artist_album_label,
    ensure_columns,
    get_today_matching_tz,
    save_plot,
    setup_analysis_logging,
)


def run(tracks_df: pd.DataFrame, params: dict[str, Any], output_path: str) -> str:
    """This run() function is executed by the analysis engine."""

    # Set up logging for this analysis process
    setup_analysis_logging(params.get("debug", False))
    logging.debug("Starting %s analysis", os.path.basename(__file__))

    # Ensure required columns exist
    ensure_columns(tracks_df, ["Play Count", "Date Added", "Album", "Album Artist"])

    df = tracks_df.dropna(
        subset=["Play Count", "Date Added", "Album", "Album Artist"]
    ).copy()

    # Convert Play Count to numeric, fill missing values with 0
    df["Play Count"] = (
        pd.to_numeric(df["Play Count"], errors="coerce").fillna(0).astype(int)
    )
    df["Date Added"] = pd.to_datetime(df["Date Added"], errors="coerce")
    df = df.dropna(subset=["Date Added"])

    # For each album, get the sum of play counts, earliest date added, and artist
    album_stats = (
        df.groupby(["Album", "Album Artist"])
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

    # Create artist: album labels with italicized album names
    window["Label"] = window.apply(
        lambda row: create_artist_album_label(row["Album Artist"], row["Album"]), axis=1
    )

    # Set figure height dynamically based on number of rows
    plt.figure(figsize=(8, max(2, len(window) * 0.35)))

    # Plot the results
    window[::-1].plot(
        kind="barh",
        x="Label",
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
