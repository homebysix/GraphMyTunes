"""track_play_ratio.py

Show the top N tracks by highest ratio of plays to skips.
Tracks with zero skips are assigned a ratio based on play count + 1 to handle division by zero.
"""

from typing import Any, Dict

import matplotlib.pyplot as plt
import pandas as pd

from src.analysis._utils_ import create_artist_track_label, ensure_columns, save_plot


def run(tracks_df: pd.DataFrame, params: Dict[str, Any], output_path: str) -> str:
    """This run() function is executed by the analysis engine."""

    ensure_columns(tracks_df, ["Name", "Artist", "Play Count", "Skip Count"])

    df = tracks_df.dropna(subset=["Name", "Artist", "Play Count", "Skip Count"]).copy()

    # Convert Play Count and Skip Count to numeric, fill missing values with 0
    df["Play Count"] = (
        pd.to_numeric(df["Play Count"], errors="coerce").fillna(0).astype(int)
    )
    df["Skip Count"] = (
        pd.to_numeric(df["Skip Count"], errors="coerce").fillna(0).astype(int)
    )

    # Only consider tracks that have been played at least once
    df = df[df["Play Count"] > 0]

    # Calculate play-to-skip ratio
    # For tracks with 0 skips, use Play Count + 1 to represent a high ratio
    # For tracks with skips, use the actual ratio
    df["Play Ratio"] = df.apply(
        lambda row: (
            row["Play Count"] + 1
            if row["Skip Count"] == 0
            else row["Play Count"] / row["Skip Count"]
        ),
        axis=1,
    )

    # Get top N tracks by play ratio
    window = df.nlargest(params["top"], "Play Ratio")

    # Create artist: track labels
    window["Track Label"] = window.apply(
        lambda row: create_artist_track_label(row["Artist"], row["Name"]), axis=1
    )

    # Sort by ratio ascending for horizontal bar chart (lowest at bottom)
    window = window.sort_values("Play Ratio", ascending=True)

    # Set figure height dynamically based on number of rows
    plt.figure(figsize=(8, max(2, len(window) * 0.35)))

    # Plot the data
    window.plot(
        kind="barh",
        x="Track Label",
        y="Play Ratio",
        color=plt.get_cmap("tab10").colors,
        edgecolor="black",
        legend=False,
        ax=plt.gca(),
    )
    plt.xlabel("Play-to-Skip Ratio")
    plt.ylabel("Track")
    title = f"Top {params['top']} Tracks by Play-to-Skip Ratio"
    save_plot(title, output_path, ext="png", dpi=300)

    return f"{output_path}.png"
