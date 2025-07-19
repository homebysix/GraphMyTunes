"""rating_playtime.py

Plot the sum of play time of all tracks grouped by star rating (0
through 5). Play time is calculated by track duration times play count.
Assumes iTunes stores ratings as 0, 20, 40, 60, 80, 100 (for 0-5 stars)
and duration in milliseconds ('Total Time').
"""

import logging
import os
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd

from src.analysis._utils_ import (
    ensure_columns,
    rating_to_stars,
    save_plot,
    setup_analysis_logging,
)


def run(tracks_df: pd.DataFrame, params: dict[str, Any], output_path: str) -> str:
    """This run() function is executed by the analysis engine."""

    # Set up logging for this analysis process
    setup_analysis_logging(params.get("debug", False))
    logging.debug("Starting %s analysis", os.path.basename(__file__))

    # Ensure required columns exist
    ensure_columns(tracks_df, ["Rating", "Play Count", "Total Time"])

    star_ratings = rating_to_stars(tracks_df["Rating"])

    # Convert Play Count and Total Time to numeric, fill missing values with 0
    play_counts = pd.to_numeric(tracks_df["Play Count"], errors="coerce").fillna(0)
    total_times = pd.to_numeric(tracks_df["Total Time"], errors="coerce").fillna(0)

    # Calculate total play time per track in hours
    play_time_hours = (play_counts * total_times) / (1000 * 60 * 60)

    # Group by star rating and sum play times
    window = (
        pd.DataFrame(
            {"Star Rating": star_ratings, "Play Time (Hours)": play_time_hours}
        )
        .groupby("Star Rating")["Play Time (Hours)"]
        .sum()
        .reindex(range(0, 6), fill_value=0)
    )

    # Set figure width dynamically based on number of columns
    plt.figure(figsize=(max(8, len(window) * 0.35), 6))

    # Plot the results
    window.plot(
        kind="bar",
        color=plt.get_cmap("tab10").colors,
        edgecolor="black",
    )
    plt.xlabel("Star Rating")
    plt.ylabel("Total Play Time (Hours)")
    plt.xticks(
        ticks=range(0, 6),
        labels=["Unrated"] + [str(i) for i in range(1, 6)],
        rotation=0,
    )
    title = "Sum of Play Time per Star Rating"
    save_plot(title, output_path, ext="png", dpi=300)

    return f"{output_path}.png"
