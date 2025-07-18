"""bpm_tracks.py

Plot the number of tracks per BPM. Assumes the DataFrame contains a
'BPM' column.
"""

from typing import Any, Dict

import matplotlib.pyplot as plt
import pandas as pd

from src.analysis._utils_ import ensure_columns, save_plot


def run(tracks_df: pd.DataFrame, params: Dict[str, Any], output_path: str) -> str:
    """This run() function is executed by the analysis engine."""

    ensure_columns(tracks_df, ["BPM"])

    bpm_series = tracks_df["BPM"].dropna().astype(int)
    bins = range(
        int(bpm_series.min() // 10 * 10), int(bpm_series.max() // 10 * 10 + 20), 10
    )
    labels = [f"{b}-{b+9}" for b in bins[:-1]]
    bpm_binned = pd.cut(
        bpm_series, bins=bins, labels=labels, right=True, include_lowest=True
    )
    window = bpm_binned.value_counts().sort_index()

    # Set figure width dynamically based on number of columns
    plt.figure(figsize=(max(8, len(window) * 0.35), 6))

    # Plot the results
    window.plot(
        kind="bar",
        color=plt.get_cmap("tab10").colors,
        edgecolor="black",
    )
    plt.xlabel("BPM Range")
    plt.ylabel("Number of Tracks")
    title = "Number of Tracks by Beats Per Minute (BPM)"
    save_plot(title, output_path, ext="png", dpi=300)

    return f"{output_path}.png"
