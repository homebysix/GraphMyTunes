"""yearly_songs_by_plays.py

Output a table containing the top N songs by Play Count for every Year
represented by tracks in the library, and the number of plays. Skips
years with no songs associated.
"""

import logging
import os
from typing import Any

import pandas as pd

from src.analysis._utils_ import ensure_columns, setup_analysis_logging


def run(tracks_df: pd.DataFrame, params: dict[str, Any], output_path: str) -> str:
    """This run() function is executed by the analysis engine."""

    # Set up logging for this analysis process
    setup_analysis_logging(params.get("debug", False))
    logging.debug("Starting %s analysis", os.path.basename(__file__))

    # Ensure required columns exist
    ensure_columns(tracks_df, ["Year", "Name", "Play Count"])

    # Drop rows with missing or invalid years, play counts, names, artists, or albums
    df = tracks_df.dropna(
        subset=["Year", "Name", "Play Count", "Artist", "Album"]
    ).copy()
    df = df[df["Year"].apply(lambda x: isinstance(x, (int, float)))]
    df["Year"] = df["Year"].astype(int)

    # Convert Play Count to numeric, fill missing values with 0
    df["Play Count"] = (
        pd.to_numeric(df["Play Count"], errors="coerce").fillna(0).astype(int)
    )

    # Find the top N songs by play count for each year, including Artist and Album
    top_songs = (
        df.sort_values(["Year", "Play Count"], ascending=[True, False])
        .groupby("Year")
        .head(params["top"])
        .loc[:, ["Year", "Name", "Artist", "Album", "Play Count"]]
    )

    # If more than one song per year is requested, add a rank column
    if params["top"] > 1:
        top_songs.insert(1, "Rank", top_songs.groupby("Year").cumcount() + 1)

    # Save as CSV table
    top_songs.to_csv(f"{output_path}.csv", index=False)

    return f"{output_path}.csv"
