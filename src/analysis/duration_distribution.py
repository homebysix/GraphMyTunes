"""duration_distribution.py

Produce a histogram showing the frequency of song durations (using the
'Total Time' field) in 30 second intervals. 'Total Time' is assumed to
be in milliseconds.
"""

from typing import Any, Dict

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.analysis._utils_ import (
    ensure_columns,
    save_plot,
    sec_to_human_readable,
    setup_analysis_logging,
)


def run(tracks_df: pd.DataFrame, params: Dict[str, Any], output_path: str) -> str:
    """This run() function is executed by the analysis engine."""

    # Set up logging for this analysis process
    setup_analysis_logging(params.get("debug", False))

    # Ensure required columns exist
    ensure_columns(tracks_df, ["Total Time"])

    # Convert duration from milliseconds to seconds
    durations_sec = (
        pd.to_numeric(tracks_df["Total Time"], errors="coerce").dropna() / 1000
    )
    # Define 30 second bins, omitting outliers beyond the 99th percentile
    upper_limit = durations_sec.quantile(0.99)
    filtered_durations = durations_sec[durations_sec <= upper_limit]
    max_duration = filtered_durations.max()
    bins = np.arange(0, max_duration + 30, 30)

    plt.figure(figsize=(8, 6))
    plt.hist(
        filtered_durations,
        bins=bins,
        color=plt.get_cmap("tab10")(0),  # Use a single color for the dataset
        edgecolor="black",
    )

    # Format x-tick labels using sec_to_human_readable()

    xticks = np.arange(0, max_duration + 1, 60)
    xtick_labels = [sec_to_human_readable(int(x)) for x in xticks]
    plt.xticks(xticks, xtick_labels)

    plt.xlabel("Duration")
    plt.ylabel("Number of Tracks")
    title = "Distribution of Song Durations (≤99th percentile)"
    save_plot(title, output_path, ext="png", dpi=300)

    return f"{output_path}.png"
