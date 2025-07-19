"""artist_plays.py

Show the total play count for all tracks by each artist.
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
    ensure_columns(tracks_df, ["Artist", "Play Count"])

    df = tracks_df.dropna(subset=["Artist", "Play Count"]).copy()

    # Convert Play Count to numeric, fill missing values with 0
    df["Play Count"] = (
        pd.to_numeric(df["Play Count"], errors="coerce").fillna(0).astype(int)
    )

    # Sum play count by artist and limit to top N
    window = (
        df.groupby("Artist")["Play Count"]
        .sum()
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
    plt.xlabel("Total Play Count")
    title = f"Top {params['top']} Artists by Play Count"
    save_plot(title, output_path, ext="png", dpi=300)

    return f"{output_path}.png"
