"""genre_avg_rating.py

Show the top N genres based on the average rating of all tracks in that
genre. Assumes iTunes ratings are 0-100 and converts to 0-5 stars.
"""

import logging
import os
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd

from src.analysis._utils_ import ensure_columns, save_plot, setup_analysis_logging


def run(tracks_df: pd.DataFrame, params: dict[str, Any], output_path: str) -> str:
    """This run() function is executed by the analysis engine."""

    # Set up logging for this analysis process
    setup_analysis_logging(params.get("debug", False))
    logging.debug("Starting %s analysis", os.path.basename(__file__))

    # Ensure required columns exist
    ensure_columns(tracks_df, ["Genre", "Rating"])

    # Fill unrated tracks (NaN) with 0
    tracks_df["Rating"] = tracks_df["Rating"].fillna(0)

    # Group by genre, calculate average rating and track count
    genre_stats = (
        tracks_df.groupby("Genre")
        .agg(avg_rating=("Rating", "mean"), track_count=("Rating", "count"))
        .reset_index()
    )

    # Filter genres with at least one rated track and avg_rating > 0
    genre_stats = genre_stats[genre_stats["avg_rating"] > 0]

    # Convert average rating from 0-100 to 0-5 stars
    genre_stats["avg_rating_stars"] = genre_stats["avg_rating"] / 20

    # Get top N genres by average rating
    window = genre_stats.sort_values("avg_rating_stars", ascending=False).head(
        params["top"]
    )

    # Set figure height dynamically based on number of rows
    plt.figure(figsize=(8, max(2, len(window) * 0.35)))

    # Plot the data
    window.plot(
        kind="barh",
        x="Genre",
        y="avg_rating_stars",
        color=plt.get_cmap("tab10").colors,
        edgecolor="black",
        legend=False,
        ax=plt.gca(),
    )
    plt.xlabel("Average Rating (Stars)")
    plt.xlim(0, 5)
    plt.gca().invert_yaxis()  # Highest rated at the top
    title = f"Top {params['top']} Genres by Average Rating"
    save_plot(title, output_path, ext="png", dpi=300)

    return f"{output_path}.png"
