"""genre_tracks_pie.py

Show the distribution of tracks across different genres as a pie chart.
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
    ensure_columns(tracks_df, ["Genre"])

    genre_tracks = tracks_df["Genre"].value_counts()

    # Calculate percentages to identify genres < 0.5%
    total_tracks = len(tracks_df)
    genre_percentages = (genre_tracks / total_tracks) * 100

    # Separate genres >= 0.5% from those < 0.5%
    major_genres = genre_tracks[genre_percentages >= 0.5]
    minor_genres = genre_tracks[genre_percentages < 0.5]

    # Combine minor genres into "Other"
    if len(minor_genres) > 0:
        other_count = minor_genres.sum()
        major_genres["Other"] = other_count

    # Sort with "Other" last
    if "Other" in major_genres.index:
        other_value = major_genres["Other"]
        major_genres_without_other = major_genres.drop("Other").sort_values(
            ascending=True
        )
        genre_tracks = pd.concat(
            [major_genres_without_other, pd.Series({"Other": other_value})]
        )
    else:
        genre_tracks = major_genres.sort_values(ascending=True)

    # Plot the pie chart
    plt.figure(figsize=(8, 8))

    # Custom function to only show value labels for slices >= 1.0%
    def autopct_format(pct: float) -> str:
        return f"{pct:.1f}%" if pct >= 1.0 else ""

    genre_tracks.plot(
        kind="pie",
        autopct=autopct_format,
        startangle=140,
        legend=False,
        pctdistance=0.85,
    )
    plt.ylabel("")
    title = "Song Distribution by Genre"
    save_plot(title, output_path, ext="png", dpi=300)

    return f"{output_path}.png"
