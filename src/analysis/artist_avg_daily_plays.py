"""artist_avg_daily_plays.py

Graph the top N artists based on average daily plays:
Sum of Play Count per artist divided by number of days since the earliest 'Date Added' for any track by the artist.
"""

import logging
import os
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd

from src.analysis._utils_ import (
    ensure_columns,
    get_today_matching_tz,
    save_plot,
    setup_analysis_logging,
    trim_label,
)


def run(tracks_df: pd.DataFrame, params: dict[str, Any], output_path: str) -> str:
    """This run() function is executed by the analysis engine."""

    # Set up logging for this analysis process
    setup_analysis_logging(params.get("debug", False))
    logging.debug("Starting %s analysis", os.path.basename(__file__))

    # Ensure required columns exist
    ensure_columns(tracks_df, ["Play Count", "Date Added", "Artist"])

    df = tracks_df.dropna(subset=["Play Count", "Date Added", "Artist"]).copy()

    # Convert Play Count to numeric, fill missing values with 0
    df["Play Count"] = (
        pd.to_numeric(df["Play Count"], errors="coerce").fillna(0).astype(int)
    )
    df["Date Added"] = pd.to_datetime(df["Date Added"], errors="coerce")
    df = df.dropna(subset=["Date Added"])

    # For each artist, get the sum of play counts and the earliest date added
    artist_stats = (
        df.groupby("Artist")
        .agg(
            Total_Play_Count=("Play Count", "sum"),
            Earliest_Date_Added=("Date Added", "min"),
        )
        .reset_index()
    )

    today = get_today_matching_tz(df["Date Added"])

    artist_stats["Days In Library"] = (
        today - artist_stats["Earliest_Date_Added"].dt.floor("D")
    ).dt.days.clip(lower=1)
    artist_stats["Avg Daily Plays"] = (
        artist_stats["Total_Play_Count"] / artist_stats["Days In Library"]
    )

    # Get top N artists by average daily plays
    window = artist_stats.sort_values("Avg Daily Plays", ascending=False).head(
        params["top"]
    )

    # Trim long names for top artists
    window["Artist"] = window["Artist"].apply(trim_label)

    # Set figure height dynamically based on number of rows
    plt.figure(figsize=(8, max(2, len(window) * 0.35)))

    window[::-1].plot(
        kind="barh",
        x="Artist",
        y="Avg Daily Plays",
        color=plt.get_cmap("tab10").colors,
        edgecolor="black",
        legend=False,
        ax=plt.gca(),
    )
    plt.xlabel("Average Daily Plays")
    title = f"Top {params['top']} Artists by Average Daily Plays"
    save_plot(title, output_path, ext="png", dpi=300)

    return f"{output_path}.png"
