"""genre_plays.py

Plot the total play count for all tracks grouped by genre.
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
    ensure_columns(tracks_df, ["Genre", "Play Count"])

    window = (
        tracks_df.groupby("Genre")["Play Count"]
        .sum()
        .sort_values(ascending=True)
        .tail(params["top"])
    )

    # Set figure height dynamically based on number of rows
    plt.figure(figsize=(8, max(2, len(window) * 0.35)))

    # Plot the results
    window.plot(
        kind="barh",
        color=plt.get_cmap("tab10").colors,
        edgecolor="black",
        legend=False,
    )
    plt.ylabel("Genre")
    plt.xlabel("Play Count")
    title = f"Top {params['top']} Genres by Play Count"
    save_plot(title, output_path, ext="png", dpi=300)

    return f"{output_path}.png"
