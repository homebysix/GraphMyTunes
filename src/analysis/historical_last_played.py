"""historical_last_played.py

Graph the last played date of tracks imported per quarter over time.
"""

from typing import Any, Dict

import matplotlib.pyplot as plt
import pandas as pd

from src.analysis._utils_ import ensure_columns, save_plot


def run(tracks_df: pd.DataFrame, params: Dict[str, Any], output_path: str) -> str:
    """This run() function is executed by the analysis engine."""

    ensure_columns(tracks_df, ["Play Date UTC"])

    # Ensure "Play Date UTC" is datetime
    tracks_df["Play Date UTC"] = pd.to_datetime(tracks_df["Play Date UTC"])

    # Group by quarter and count tracks
    window = tracks_df.set_index("Play Date UTC").resample("QE").size()

    # Set figure width dynamically based on number of columns
    plt.figure(figsize=(max(6, len(window) * 0.35), 6))

    # Plot the results
    ax = window.plot(
        kind="bar",
        color=plt.get_cmap("tab10").colors,
        edgecolor="black",
        legend=False,
    )
    plt.ylim(bottom=0)  # Set minimum y-axis at zero

    # Only label the first quarter of each year
    labels = []
    for idx in window.index:
        if idx.quarter == 1:
            labels.append(idx.year)
        else:
            labels.append("")
    ax.set_xticklabels(labels, rotation=0, ha="center")

    # Reverse the x-axis to have most recent quarter at the right
    # (optional, comment out if not desired)
    # ax.invert_xaxis()

    plt.ylabel("Number of Tracks Last Played")
    plt.xlabel("Quarter")
    title = "Tracks Last Played Per Quarter Over Time"
    save_plot(title, output_path, ext="png", dpi=300)

    return f"{output_path}.png"
