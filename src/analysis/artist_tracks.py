"""artist_tracks.py

Show the top N artists by total number of tracks in the library.
"""

from typing import Any, Dict

import matplotlib.pyplot as plt
import pandas as pd

from src.analysis._utils_ import ensure_columns, save_plot, setup_analysis_logging


def run(tracks_df: pd.DataFrame, params: Dict[str, Any], output_path: str) -> str:
    """This run() function is executed by the analysis engine."""

    # Set up logging for this analysis process
    setup_analysis_logging(params.get("debug", False))

    # Ensure required columns exist
    ensure_columns(tracks_df, ["Artist"])

    df = tracks_df.dropna(subset=["Artist"]).copy()

    # Count tracks by artist and limit to top N
    window = (
        df.groupby("Artist")
        .size()
        .sort_values(ascending=False)
        .head(params["top"])
        .sort_values(ascending=True)
    )

    # Set figure height dynamically based on number of rows
    plt.figure(figsize=(8, max(2, len(window) * 0.35)))

    # Plot the data
    window.plot(
        kind="barh",
        color=plt.get_cmap("tab10").colors,
        edgecolor="black",
        legend=False,
    )
    plt.ylabel("Artist")
    plt.xlabel("Number of Tracks")
    title = f"Top {params['top']} Artists by Track Count"
    save_plot(title, output_path, ext="png", dpi=300)

    return f"{output_path}.png"
