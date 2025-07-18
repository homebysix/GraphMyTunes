"""play_count_distribution.py

Plot a histogram showing the distribution of play counts across all
tracks.
"""

from typing import Any, Dict

import matplotlib.pyplot as plt
import pandas as pd

from src.analysis._utils_ import ensure_columns, save_plot


def run(tracks_df: pd.DataFrame, params: Dict[str, Any], output_path: str) -> str:
    """This run() function is executed by the analysis engine."""

    ensure_columns(tracks_df, ["Play Count"])

    # Convert Play Count to numeric, fill missing values with 0
    play_counts = tracks_df["Play Count"].fillna(0).astype(int)

    # Plot the results
    plt.figure(figsize=(8, 6))
    plt.hist(
        play_counts,
        bins=range(0, play_counts.max() + 2),
        color=plt.get_cmap("tab10")(0),  # Use a single color for the dataset
        edgecolor="black",
    )
    plt.xlabel("Play Count")
    plt.xlim(left=0)  # Ensure x-axis minimum is 0
    plt.ylabel("Number of Tracks")
    title = "Distribution of Play Counts"
    save_plot(title, output_path, ext="png", dpi=300)

    return f"{output_path}.png"
