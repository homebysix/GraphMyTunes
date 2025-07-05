"""historical_play_counts.py

Graph the total play counts of tracks imported per quarter over time,
"""

from typing import Any, Dict

import matplotlib.pyplot as plt
import pandas as pd

from src.analysis._utils_ import ensure_columns, save_plot


def run(tracks_df: pd.DataFrame, params: Dict[str, Any], output_path: str) -> str:
    """This run() function is executed by the analysis engine."""

    ensure_columns(tracks_df, ["Date Added", "Play Count"])

    # Ensure "Date Added" is datetime
    tracks_df["Date Added"] = pd.to_datetime(tracks_df["Date Added"])

    # Group by quarter and sum play counts of tracks imported in each quarter
    window = (
        tracks_df.set_index("Date Added").resample("QE")["Play Count"].sum().fillna(0)
    )

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

    plt.ylabel("Total Play Counts")
    plt.xlabel("Quarter")
    title = "Total Play Counts of Tracks Imported Per Quarter Over Time"
    save_plot(title, output_path, ext="png", dpi=300)

    return f"{output_path}.png"
