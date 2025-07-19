"""bitrate_distribution.py

Produce a histogram showing the frequency of song bitrates (using the
'Bit Rate' field).
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
    ensure_columns(tracks_df, ["Bit Rate"])

    # Convert Bit Rate to numeric, drop NaNs
    bitrates = pd.to_numeric(tracks_df["Bit Rate"], errors="coerce").dropna()
    # Omit outliers beyond the 99th percentile
    upper_limit = bitrates.quantile(0.99)
    filtered_bitrates = bitrates[bitrates <= upper_limit]
    max_bitrate = filtered_bitrates.max()
    min_bitrate = filtered_bitrates.min()
    # Define bins (e.g., 16 kbps steps)
    bins = np.arange(min_bitrate, max_bitrate + 16, 16)
    plt.figure(figsize=(8, 6))
    plt.hist(
        filtered_bitrates,
        bins=bins,
        color=plt.get_cmap("tab10")(0),  # Use a single color for the dataset
        edgecolor="black",
    )
    plt.xlabel("Bit Rate (kbps)")
    plt.ylabel("Number of Tracks")
    plt.xlim(0, 2000)
    plt.xticks(np.arange(0, 2001, 64), rotation=45)
    title = "Distribution of Song Bit Rates (≤99th percentile)"
    save_plot(title, output_path, ext="png", dpi=300)

    return f"{output_path}.png"
