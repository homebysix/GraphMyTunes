"""album_skips.py

Show the total skip count for all tracks in each album.
"""

import logging
import os
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd

from src.analysis._utils_ import (
    create_artist_album_label,
    ensure_columns,
    save_plot,
    setup_analysis_logging,
)


def run(tracks_df: pd.DataFrame, params: dict[str, Any], output_path: str) -> str:
    """This run() function is executed by the analysis engine."""

    # Set up logging for this analysis process
    setup_analysis_logging(params.get("debug", False))
    logging.debug("Starting %s analysis", os.path.basename(__file__))

    # Ensure required columns exist
    ensure_columns(tracks_df, ["Album", "Album Artist", "Skip Count"])

    df = tracks_df.dropna(subset=["Album", "Album Artist", "Skip Count"]).copy()

    # Convert Skip Count to numeric, fill missing values with 0
    df["Skip Count"] = (
        pd.to_numeric(df["Skip Count"], errors="coerce").fillna(0).astype(int)
    )

    # Create artist: album labels with italicized album names
    df["Label"] = df.apply(
        lambda row: create_artist_album_label(row["Album Artist"], row["Album"]), axis=1
    )

    # Sum skip count by label and get top N
    window = (
        df.groupby("Label")["Skip Count"]
        .sum()
        .sort_values(ascending=True)
        .tail(params["top"])
    )

    # Set figure height dynamically based on number of rows
    plt.figure(figsize=(8, max(2, len(window) * 0.35)))

    # Plot the data
    window.plot(
        kind="barh",
        color=plt.get_cmap("tab10").colors,
        edgecolor="black",
    )
    plt.ylabel("Album")
    plt.xlabel("Total Skip Count")
    title = f"Top {params['top']} Albums by Skip Count"
    save_plot(title, output_path, ext="png", dpi=300)

    return f"{output_path}.png"
