"""album_avg_rating.py

For all albums with more than 1 track, calculate the average rating of
all tracks on the album (including unrated tracks as 0), and graph the
top N by average rating, omitting albums with an average rating of
zero. Assumes iTunes ratings are 0-100 and converts to 0-5 stars.
"""

from typing import Any, Dict

import matplotlib.pyplot as plt
import pandas as pd

from src.analysis._utils_ import ensure_columns, save_plot, trim_label


def run(tracks_df: pd.DataFrame, params: Dict[str, Any], output_path: str) -> str:
    """This run() function is executed by the analysis engine."""

    ensure_columns(tracks_df, ["Rating", "Album"])

    # Convert Rating to numeric, fill missing values with 0
    tracks_df["Rating"] = tracks_df["Rating"].fillna(0)

    # Group by album, calculate average rating and track count
    album_stats = (
        tracks_df.groupby("Album")
        .agg(avg_rating=("Rating", "mean"), track_count=("Rating", "count"))
        .reset_index()
    )

    # Filter albums with more than 1 track and avg_rating > 0
    album_stats = album_stats[
        (album_stats["track_count"] > 1) & (album_stats["avg_rating"] > 0)
    ]

    # Convert average rating from 0-100 to 0-5 stars
    album_stats["avg_rating_stars"] = album_stats["avg_rating"] / 20

    # Get top N albums by average rating
    window = album_stats.sort_values("avg_rating_stars", ascending=False).head(
        params["top"]
    )

    # Trim long names
    window["Album (Trimmed)"] = window["Album"].apply(trim_label)

    # Set figure height dynamically based on number of rows
    plt.figure(figsize=(6, max(2, len(window) * 0.35)))

    # Plot the data, if there is data to plot
    if window.empty:
        plt.text(
            0.5,
            0.5,
            "No albums with more than 1 track and non-zero average rating.",
            horizontalalignment="center",
            verticalalignment="center",
            fontsize=12,
        )
        plt.axis("off")
    else:
        window.plot(
            kind="barh",
            x="Album (Trimmed)",
            y="avg_rating_stars",
            color=plt.get_cmap("tab10").colors,
            edgecolor="black",
            legend=False,
            ax=plt.gca(),
        )
        plt.xlabel("Average Rating (Stars)")
        plt.xlim(0, 5)
        plt.gca().invert_yaxis()  # Highest rated at the top

    title = f"Top {params['top']} Albums by Average Track Rating"
    save_plot(title, output_path, ext="png", dpi=300)

    return f"{output_path}.png"
