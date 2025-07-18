"""bpm_plays.py

Plot the sum of play counts of all tracks grouped by BPM intervals of
10.
"""

from typing import Any, Dict

import matplotlib.pyplot as plt
import pandas as pd

from src.analysis._utils_ import ensure_columns, save_plot


def run(tracks_df: pd.DataFrame, params: Dict[str, Any], output_path: str) -> str:
    """This run() function is executed by the analysis engine."""

    ensure_columns(tracks_df, ["BPM", "Play Count"])

    # Drop tracks with missing or zero BPM
    valid_tracks = tracks_df[(tracks_df["BPM"].notna()) & (tracks_df["BPM"] != 0)]
    bpm = valid_tracks["BPM"].astype(int)

    # Convert Play Count to numeric, fill missing values with 0
    play_counts = valid_tracks["Play Count"].fillna(0)

    # Create BPM bins (intervals of 10)
    bpm_bins = (bpm // 10) * 10
    bpm_bin_labels = bpm_bins.astype(str) + "-" + (bpm_bins + 9).astype(str)

    # Sum play counts grouped by BPM bins
    window = (
        pd.DataFrame({"BPM Bin": bpm_bin_labels, "Play Count": play_counts})
        .groupby("BPM Bin")["Play Count"]
        .sum()
        .sort_index(key=lambda x: x.str.extract(r"^(\d+)").astype(int)[0])
    )

    # Set figure width dynamically based on number of columns
    plt.figure(figsize=(max(8, len(window) * 0.35), 6))

    # Plot the results
    window.plot(
        kind="bar",
        color=plt.get_cmap("tab10").colors,
        edgecolor="black",
    )
    plt.xlabel("BPM Range")
    plt.ylabel("Total Play Count")
    title = "Sum of Play Counts by Beats Per Minute (BPM)"
    save_plot(title, output_path, ext="png", dpi=300)

    return f"{output_path}.png"
