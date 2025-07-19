"""artist_play_ratio.py

Show the top N artists by highest ratio of plays to skips.
Artists with zero skips are assigned a ratio based on play count + 1 to handle division by zero.
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

    # Calculate play-to-skip ratio
    # For artists with 0 skips, use Play Count + 1 to represent a high ratio
    # For artists with skips, use the actual ratio
    artist_stats["Play Ratio"] = artist_stats.apply(
        lambda row: (
            row["Play Count"] + 1
            if row["Skip Count"] == 0
            else row["Play Count"] / row["Skip Count"]
        ),
        axis=1,
    )

    # Get top N artists by play ratio
    window = artist_stats.nlargest(params["top"], "Play Ratio")

    # Sort by ratio ascending for horizontal bar chart (lowest at bottom)
    window = window.sort_values("Play Ratio", ascending=True)

    # Set figure height dynamically based on number of rows
    plt.figure(figsize=(8, max(2, len(window) * 0.35)))

    # Plot the data
    window.plot(
        kind="barh",
        x="Artist",
        y="Play Ratio",
        color=plt.get_cmap("tab10").colors,
        edgecolor="black",
        legend=False,
        ax=plt.gca(),
    )
    plt.xlabel("Play-to-Skip Ratio")
    plt.ylabel("Artist")
    title = f"Top {params['top']} Artists by Play-to-Skip Ratio"
    save_plot(title, output_path, ext="png", dpi=300)

    return f"{output_path}.png"
