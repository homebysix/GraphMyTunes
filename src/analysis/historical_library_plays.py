"""historical_library_plays.py

Graph the cumulative sum of play counts of tracks in the library over
time, based on the 'Date Added' field, grouped by quarter.
"""

from typing import Any, Dict

import matplotlib.pyplot as plt
import pandas as pd

from src.analysis._utils_ import ensure_columns, save_plot, setup_analysis_logging


def run(tracks_df: pd.DataFrame, params: Dict[str, Any], output_path: str) -> str:
    """This run() function is executed by the analysis engine."""

    # Set up logging for this analysis process
    setup_analysis_logging(params.get("debug", False))

    # Ensure required columns exist
    ensure_columns(tracks_df, ["Date Added", "Play Count"])

    # Convert 'Date Added' to datetime and drop rows with missing data
    df = tracks_df.dropna(subset=["Date Added", "Play Count"]).copy()
    df["Date Added"] = pd.to_datetime(df["Date Added"], errors="coerce")
    df = df.dropna(subset=["Date Added", "Play Count"])
    df = df.sort_values("Date Added")

    # Group by quarter and sum play counts, then take cumulative sum
    df = df.set_index("Date Added")
    quarterly = df["Play Count"].resample("QE").sum().cumsum()

    # Plot the results
    plt.figure(figsize=(12, 6))
    ax = plt.gca()
    quarterly.plot(ax=ax, color=plt.get_cmap("tab10").colors)
    ax.fill_between(
        quarterly.index,
        quarterly.values,
        color=plt.get_cmap("tab10").colors[0],
        alpha=0.2,
    )
    ax.set_ylim(bottom=0)
    plt.xlabel("Date (Quarter)")
    plt.ylabel("Cumulative Play Count")
    title = "Cumulative Play Count by Date Added (Quarterly)"
    save_plot(title, output_path, ext="png", dpi=300)

    return f"{output_path}.png"
