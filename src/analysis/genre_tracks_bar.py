"""genre_tracks_bar.py

Plot the number of tracks in each genre as a horizontal bar chart.
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
    ensure_columns(tracks_df, ["Genre"])

    window = (
        tracks_df["Genre"]
        .value_counts()
        .sort_values(ascending=True)
        .tail(params["top"])
    )

    # Set figure height dynamically based on number of rows
    plt.figure(figsize=(8, max(2, len(window) * 0.35)))

    # Plot the bar chart
    window.plot(
        kind="barh",
        color=plt.get_cmap("tab10").colors,
        edgecolor="black",
        legend=False,
    )
    plt.ylabel("Genre")
    plt.xlabel("Song Count")
    title = f"Top {params['top']} Genres by Song Count"
    save_plot(title, output_path, ext="png", dpi=300)

    return f"{output_path}.png"
