"""track_minplayed.py

Create a bar chart showing how many tracks have been played at least N times
for x values in the 99th percentile of play counts.
"""

import logging
import os
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.analysis._utils_ import ensure_columns, save_plot, setup_analysis_logging


def run(tracks_df: pd.DataFrame, params: dict[str, Any], output_path: str) -> str:
    """This run() function is executed by the analysis engine."""

    # Set up logging for this analysis process
    setup_analysis_logging(params.get("debug", False))
    logging.debug("Starting %s analysis", os.path.basename(__file__))

    # Ensure required columns exist
    ensure_columns(tracks_df, ["Play Count"])

    # Convert Play Count to numeric, fill missing values with 0
    play_counts = tracks_df["Play Count"].fillna(0).astype(int)

    # Remove tracks with 0 plays for percentile calculation
    non_zero_plays = play_counts[play_counts > 0]

    if len(non_zero_plays) == 0:
        raise ValueError("No tracks with play counts > 0 found")

    # Calculate the 99th percentile of play counts
    percentile_99 = np.percentile(non_zero_plays, 99)

    # Create x values from 1 to the 99th percentile
    max_plays = int(percentile_99)
    x_values = np.arange(1, max_plays + 1)

    # Calculate percentage of tracks that have been played at least N times for each x value
    total_tracks = len(play_counts)
    y_values = []
    for n in x_values:
        count = (play_counts >= n).sum()
        percentage = (count / total_tracks) * 100
        y_values.append(percentage)

    # Create the bar chart
    plt.figure(figsize=(8, 6))
    plt.bar(x_values, y_values, color=plt.get_cmap("tab10")(0), edgecolor="black")

    plt.xlabel("Minimum Play Count")
    plt.ylabel("Percentage of tracks")
    plt.ylim(0, 100)

    # Set x-axis to show all values if reasonable, otherwise use automatic ticks
    if len(x_values) <= 50:
        plt.xticks(x_values[:: max(1, len(x_values) // 20)])  # Show every nth tick

    title = "Percentage of Tracks Played At Least X Times (P$_{99}$)"
    save_plot(title, output_path, ext="png", dpi=300)

    return f"{output_path}.png"
