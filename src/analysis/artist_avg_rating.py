"""artist_avg_rating.py

For all artists with more than 1 track, calculate the average rating of
all tracks by the artist (including unrated tracks as 0), and graph the
top N by average rating, omitting artists with an average rating of
zero. Assumes iTunes ratings are 0-100 and converts to 0-5 stars.
"""

import logging
import os
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd

from src.analysis._utils_ import (
    ensure_columns,
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
    ensure_columns(tracks_df, ["Artist", "Rating"])

    # Convert Rating to numeric, fill missing values with 0
    tracks_df["Rating"] = tracks_df["Rating"].fillna(0)

    # Group by artist, calculate average rating and track count
    artist_stats = (
        tracks_df.groupby("Artist")
        .agg(avg_rating=("Rating", "mean"), track_count=("Rating", "count"))
        .reset_index()
    )

    # Filter artists with more than 1 track and avg_rating > 0
    artist_stats = artist_stats[
        (artist_stats["track_count"] > 1) & (artist_stats["avg_rating"] > 0)
    ]

    # Convert average rating from 0-100 to 0-5 stars
    artist_stats["avg_rating_stars"] = artist_stats["avg_rating"] / 20

    # Get top N artists by average rating
    window = artist_stats.sort_values("avg_rating_stars", ascending=False).head(
        params["top"]
    )

    # Set figure height dynamically based on number of rows
    plt.figure(figsize=(8, max(2, len(window) * 0.35)))

    # Trim artist names for better readability
    window["Artist (Trimmed)"] = window["Artist"].apply(trim_label)

    # Plot the data, if there is data to plot
    if window.empty:
        plt.text(
            0.5,
            0.5,
            "No artists with more than 1 track and non-zero average rating.",
            horizontalalignment="center",
            verticalalignment="center",
            fontsize=12,
        )
        plt.axis("off")
    else:
        window.plot(
            kind="barh",
            x="Artist (Trimmed)",
            y="avg_rating_stars",
            color=plt.get_cmap("tab10").colors,
            edgecolor="black",
            legend=False,
            ax=plt.gca(),
        )
        plt.xlabel("Average Rating (Stars)")
        plt.xlim(0, 5)
        plt.gca().invert_yaxis()  # Highest rated at the top

    title = f"Top {params['top']} Artists by Average Track Rating"
    save_plot(title, output_path, ext="png", dpi=300)

    return f"{output_path}.png"
