"""kind_distribution.py

Produce a histogram (bar chart) showing the frequency of track 'Kind'.
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
    ensure_columns(tracks_df, ["Kind"])

    window = tracks_df["Kind"].value_counts().sort_values(ascending=False)

    # Set figure width dynamically based on number of columns
    plt.figure(figsize=(max(8, len(window) * 0.35), 6))

    # Plot the results
    window.plot(
        kind="bar",
        color=plt.get_cmap("tab10").colors,
        edgecolor="black",
    )
    plt.xlabel("Kind")
    plt.ylabel("Number of Tracks")
    plt.xticks(rotation=45, ha="right")
    title = "Distribution of Track Kind"
    save_plot(title, output_path, ext="png", dpi=300)

    return f"{output_path}.png"
