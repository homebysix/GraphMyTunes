"""rating_plays.py

Plot the sum of play counts of all tracks grouped by star rating (0
through 5). Assumes iTunes stores ratings as 0, 20, 40, 60, 80, 100 (for
0-5 stars).
"""

from typing import Any, Dict

import matplotlib.pyplot as plt
import pandas as pd

from src.analysis._utils_ import (
    ensure_columns,
    rating_to_stars,
    save_plot,
    setup_analysis_logging,
)


def run(tracks_df: pd.DataFrame, params: Dict[str, Any], output_path: str) -> str:
    """This run() function is executed by the analysis engine."""

    # Set up logging for this analysis process
    setup_analysis_logging(params.get("debug", False))

    # Ensure required columns exist
    ensure_columns(tracks_df, ["Rating", "Play Count"])

    star_ratings = rating_to_stars(tracks_df["Rating"])

    # Convert Play Count to numeric, fill missing values with 0
    play_counts = tracks_df["Play Count"].fillna(0)

    # Group by star rating and sum play counts
    window = (
        pd.DataFrame({"Star Rating": star_ratings, "Play Count": play_counts})
        .groupby("Star Rating")["Play Count"]
        .sum()
        .reindex(range(0, 6), fill_value=0)
    )

    # Set figure width dynamically based on number of columns
    plt.figure(figsize=(max(8, len(window) * 0.35), 6))

    # Plot the results
    window.plot(
        kind="bar",
        color=plt.get_cmap("tab10").colors,
        edgecolor="black",
    )
    plt.xlabel("Star Rating")
    plt.ylabel("Total Play Count")
    plt.xticks(
        ticks=range(0, 6),
        labels=["Unrated"] + [str(i) for i in range(1, 6)],
        rotation=0,
    )
    title = "Sum of Play Counts per Star Rating"
    save_plot(title, output_path, ext="png", dpi=300)

    return f"{output_path}.png"
