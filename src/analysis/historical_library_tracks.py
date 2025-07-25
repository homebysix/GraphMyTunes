"""historical_library_tracks.py

Graph the cumulative count of all tracks in the library over time, based
on the 'Date Added' field.
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
    ensure_columns(tracks_df, ["Date Added"])

    # Convert 'Date Added' to datetime and drop rows with missing data
    df = tracks_df.dropna(subset=["Date Added"]).copy()
    df["Date Added"] = pd.to_datetime(df["Date Added"], errors="coerce")
    df = df.dropna(subset=["Date Added"])
    df = df.sort_values("Date Added")

    # Each track is a row, so cumulative count is just a running total
    df["Track_Count"] = 1
    monthly = df.set_index("Date Added").resample("ME")["Track_Count"].sum().cumsum()

    # Plot the results
    plt.figure(figsize=(12, 6))
    ax = plt.gca()
    monthly.plot(ax=ax, color=plt.get_cmap("tab10").colors)
    ax.fill_between(
        monthly.index, monthly.values, color=plt.get_cmap("tab10").colors[0], alpha=0.3
    )
    ax.set_ylim(bottom=0)

    # Label every year on the x-axis
    years = pd.date_range(start=monthly.index.min(), end=monthly.index.max(), freq="YS")
    ax.set_xticks(years)
    ax.set_xticklabels([year.strftime("%Y") for year in years], rotation=45)

    plt.xlabel("Date")
    plt.ylabel("Total Number of Tracks")
    title = "Historical Library Track Count Over Time"
    save_plot(title, output_path, ext="png", dpi=300)

    return f"{output_path}.png"
