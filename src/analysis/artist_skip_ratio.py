"""artist_skip_ratio.py

Show the top N artists by highest ratio of skips to plays.
Artists with zero plays are excluded. Artists with zero skips have a ratio of 0.
"""

import logging
import os
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd

from src.analysis._utils_ import (
    ensure_columns,
    save_plot,
    setup_analysis_logging,
    trim_label,
)


def run(tracks_df: pd.DataFrame, params: dict[str, Any], output_path: str) -> str:
    """This run() function is executed by the analysis engine."""

    # Set up logging for this analysis process
    setup_analysis_logging(params.get("debug", False))
    logging.debug("Starting %s analysis", os.path.basename(__file__))

    # Ensure required columns exist
    ensure_columns(tracks_df, ["Artist", "Play Count", "Skip Count"])

    df = tracks_df.dropna(subset=["Artist", "Play Count", "Skip Count"]).copy()

    # Convert Play Count and Skip Count to numeric, fill missing values with 0
    df["Play Count"] = (
        pd.to_numeric(df["Play Count"], errors="coerce").fillna(0).astype(int)
    )
    df["Skip Count"] = (
        pd.to_numeric(df["Skip Count"], errors="coerce").fillna(0).astype(int)
    )

    # Only consider tracks that have been played at least once
    df = df[df["Play Count"] > 0]

    # Aggregate by artist
    artist_stats = (
        df.groupby("Artist")
        .agg({"Play Count": "sum", "Skip Count": "sum"})
        .reset_index()
    )

    # Calculate skip-to-play ratio
    # For artists with 0 skips, the ratio is 0
    # For artists with skips, use the actual ratio
    artist_stats["Skip Ratio"] = artist_stats["Skip Count"] / artist_stats["Play Count"]

    # Get top N artists by skip ratio
    window = artist_stats.nlargest(params["top"], "Skip Ratio")

    # Sort by ratio ascending for horizontal bar chart (lowest at bottom)
    window = window.sort_values("Skip Ratio", ascending=True)

    # Set figure height dynamically based on number of rows
    plt.figure(figsize=(8, max(2, len(window) * 0.35)))

    # Trim artist names for better readability
    window["Artist"] = window["Artist"].apply(trim_label)

    # Plot the data
    window.plot(
        kind="barh",
        x="Artist",
        y="Skip Ratio",
        color=plt.get_cmap("tab10").colors,
        edgecolor="black",
        legend=False,
        ax=plt.gca(),
    )
    plt.xlabel("Skip-to-Play Ratio")
    plt.ylabel("Artist")
    title = f"Top {params['top']} Artists by Skip-to-Play Ratio"
    save_plot(title, output_path, ext="png", dpi=300)

    return f"{output_path}.png"
