"""album_skip_ratio.py

Show the top N albums by highest ratio of skips to plays.
Albums with zero plays are excluded. Albums with zero skips have a ratio of 0.
"""

from typing import Any, Dict

import matplotlib.pyplot as plt
import pandas as pd

from src.analysis._utils_ import (
    create_artist_album_label,
    ensure_columns,
    save_plot,
    setup_analysis_logging,
)


def run(tracks_df: pd.DataFrame, params: Dict[str, Any], output_path: str) -> str:
    """This run() function is executed by the analysis engine."""

    # Set up logging for this analysis process
    setup_analysis_logging(params.get("debug", False))

    # Ensure required columns exist
    ensure_columns(tracks_df, ["Album", "Album Artist", "Play Count", "Skip Count"])

    df = tracks_df.dropna(
        subset=["Album", "Album Artist", "Play Count", "Skip Count"]
    ).copy()

    # Convert Play Count and Skip Count to numeric, fill missing values with 0
    df["Play Count"] = (
        pd.to_numeric(df["Play Count"], errors="coerce").fillna(0).astype(int)
    )
    df["Skip Count"] = (
        pd.to_numeric(df["Skip Count"], errors="coerce").fillna(0).astype(int)
    )

    # Only consider tracks that have been played at least once
    df = df[df["Play Count"] > 0]

    # Create artist: album labels with italicized album names
    df["Label"] = df.apply(
        lambda row: create_artist_album_label(row["Album Artist"], row["Album"]), axis=1
    )

    # Aggregate by album label
    album_stats = (
        df.groupby("Label")
        .agg({"Play Count": "sum", "Skip Count": "sum"})
        .reset_index()
    )

    # Calculate skip-to-play ratio
    # For albums with 0 skips, the ratio is 0
    # For albums with skips, use the actual ratio
    album_stats["Skip Ratio"] = album_stats["Skip Count"] / album_stats["Play Count"]

    # Get top N albums by skip ratio
    window = album_stats.nlargest(params["top"], "Skip Ratio")

    # Sort by ratio ascending for horizontal bar chart (lowest at bottom)
    window = window.sort_values("Skip Ratio", ascending=True)

    # Set figure height dynamically based on number of rows
    plt.figure(figsize=(8, max(2, len(window) * 0.35)))

    # Plot the data
    window.plot(
        kind="barh",
        x="Label",
        y="Skip Ratio",
        color=plt.get_cmap("tab10").colors,
        edgecolor="black",
        legend=False,
        ax=plt.gca(),
    )
    plt.xlabel("Skip-to-Play Ratio")
    plt.ylabel("Album")
    title = f"Top {params['top']} Albums by Skip-to-Play Ratio"
    save_plot(title, output_path, ext="png", dpi=300)

    return f"{output_path}.png"
