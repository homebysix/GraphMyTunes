"""rating_tracks.py

Plot the number of tracks per star rating (0 through 5). Assumes iTunes
stores ratings as 0, 20, 40, 60, 80, 100 (for 0-5 stars).
"""

from typing import Any, Dict

import matplotlib.pyplot as plt
import pandas as pd

from src.analysis._utils_ import ensure_columns, rating_to_stars, save_plot


def run(tracks_df: pd.DataFrame, params: Dict[str, Any], output_path: str) -> str:
    """This run() function is executed by the analysis engine."""

    ensure_columns(tracks_df, ["Rating"])

    star_ratings = rating_to_stars(tracks_df["Rating"])

    window = star_ratings.value_counts().reindex(range(0, 6), fill_value=0).sort_index()

    # Set figure width dynamically based on number of columns
    plt.figure(figsize=(max(8, len(window) * 0.35), 6))

    # Plot the results
    window.plot(
        kind="bar",
        color=plt.get_cmap("tab10").colors,
        edgecolor="black",
    )
    plt.xlabel("Star Rating")
    plt.ylabel("Number of Tracks")
    plt.xticks(
        ticks=range(0, 6),
        labels=["Unrated"] + [str(i) for i in range(1, 6)],
        rotation=0,
    )
    title = "Number of Tracks per Star Rating"
    save_plot(title, output_path, ext="png", dpi=300)

    return f"{output_path}.png"
