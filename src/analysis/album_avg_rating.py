"""album_avg_rating.py

For all albums with more than 1 track, calculate the average rating of
all tracks on the album (including unrated tracks as 0), and graph the
top N by average rating, omitting albums with an average rating of
zero. Assumes iTunes ratings are 0-100 and converts to 0-5 stars.
"""

import logging
import os
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd

from src.analysis._utils_ import (
    create_artist_album_label,
    ensure_columns,
    save_plot,
    setup_analysis_logging,
)


def run(tracks_df: pd.DataFrame, params: dict[str, Any], output_path: str) -> str:
    """This run() function is executed by the analysis engine."""

    # Set up logging for this analysis process
    setup_analysis_logging(params.get("debug", False))
    logging.debug("Starting %s analysis", os.path.basename(__file__))

    # Ensure required columns exist
    ensure_columns(tracks_df, ["Rating", "Album", "Album Artist"])

    # Convert Rating to numeric, fill missing values with 0
    tracks_df["Rating"] = tracks_df["Rating"].fillna(0)

    # Group by album and album artist, calculate average rating and track count
    album_stats = (
        tracks_df.groupby(["Album", "Album Artist"])
        .agg(avg_rating=("Rating", "mean"), track_count=("Rating", "count"))
        .reset_index()
    )

    # Filter albums with more than 1 track and avg_rating > 0
    album_stats = album_stats[
        (album_stats["track_count"] > 1) & (album_stats["avg_rating"] > 0)
    ]

    # Convert average rating from 0-100 to 0-5 stars
    album_stats["avg_rating_stars"] = album_stats["avg_rating"] / 20

    # Get top N albums by average rating
    window = (
        album_stats.sort_values("avg_rating_stars", ascending=False)
        .head(params["top"])
        .copy()
    )

    # Create artist: album labels with italicized album names
    labels = []
    for _, row in window.iterrows():
        labels.append(create_artist_album_label(row["Album Artist"], row["Album"]))
    window["Label"] = labels

    # Set figure height dynamically based on number of rows
    plt.figure(figsize=(8, max(2, len(window) * 0.35)))

    # Plot the data, if there is data to plot
    if window.empty:
        plt.text(
            0.5,
            0.5,
            "No albums with more than 1 track and non-zero average rating.",
            horizontalalignment="center",
            verticalalignment="center",
            fontsize=12,
        )
        plt.axis("off")
    else:
        window.plot(
            kind="barh",
            x="Label",
            y="avg_rating_stars",
            color=plt.get_cmap("tab10").colors,
            edgecolor="black",
            legend=False,
            ax=plt.gca(),
        )
        plt.xlabel("Average Rating (Stars)")
        plt.xlim(0, 5)
        plt.gca().invert_yaxis()  # Highest rated at the top

    title = f"Top {params['top']} Albums by Average Track Rating"
    save_plot(title, output_path, ext="png", dpi=300)

    return f"{output_path}.png"
