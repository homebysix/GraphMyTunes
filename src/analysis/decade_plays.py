"""decade_plays.py

Plot the total play count for all tracks grouped by decade.
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
    ensure_columns(tracks_df, ["Year", "Play Count"])

    # Drop rows with missing or invalid years and play counts
    tracks_df = tracks_df.dropna(subset=["Year", "Play Count"])
    tracks_df = tracks_df[
        tracks_df["Year"].apply(lambda x: isinstance(x, (int, float)))
        & tracks_df["Play Count"].apply(lambda x: isinstance(x, (int, float)))
    ]

    # Calculate decade for each track
    tracks_df["Decade"] = (tracks_df["Year"] // 10 * 10).astype(int)

    # Sum play counts per decade
    window = tracks_df.groupby("Decade")["Play Count"].sum().sort_index()

    # Add "s" to decade labels (e.g., 1990 -> "1990s")
    window.index = window.index.map(lambda d: f"{d}s")

    # Set figure width dynamically based on number of columns
    plt.figure(figsize=(max(8, len(window) * 0.35), 6))

    # Plot the results
    window.plot(
        kind="bar",
        color=plt.get_cmap("tab10").colors,
        edgecolor="black",
        legend=False,
    )
    plt.xlabel("Decade")
    plt.ylabel("Total Play Count")
    plt.xticks(rotation=45)
    title = "Total Play Count per Decade"
    save_plot(title, output_path, ext="png", dpi=300)

    return f"{output_path}.png"
