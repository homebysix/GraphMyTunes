"""library_overview.py

A few interesting stats about the music library, such as total number of tracks,
total number of artists, and total number of albums, total play time, first and
last songs added, and average playtime per day over the age of the library.
"""

import logging
import os
from datetime import datetime
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd

from src.analysis._utils_ import (
    bytes_to_human_readable,
    create_artist_track_label,
    ensure_columns,
    save_plot,
    sec_to_human_readable,
    setup_analysis_logging,
)


def run(tracks_df: pd.DataFrame, params: dict[str, Any], output_path: str) -> str:
    """This run() function is executed by the analysis engine."""

    # Set up logging for this analysis process
    setup_analysis_logging(params.get("debug", False))
    logging.debug("Starting %s analysis", os.path.basename(__file__))

    # Ensure required columns exist
    required_columns = [
        "Name",
        "Artist",
        "Album",
        "Total Time",
        "Date Added",
        "Play Count",
        "Size",
    ]
    ensure_columns(tracks_df, required_columns)

    # Calculate stats
    total_tracks = len(tracks_df)
    total_artists = tracks_df["Artist"].nunique()
    total_albums = tracks_df["Album"].nunique()
    total_play_time_sec = (
        tracks_df["Total Time"] * tracks_df["Play Count"].fillna(0)
    ).sum() / 1000  # assuming ms
    tracks_with_rating = (
        tracks_df["Rating"].notnull().sum() if "Rating" in tracks_df.columns else 0
    )
    logging.debug(
        "Basic stats calculated - tracks: %d, artists: %d, albums: %d",
        total_tracks,
        total_artists,
        total_albums,
    )
    logging.debug(
        "Total play time: %.2f seconds, rated tracks: %d",
        total_play_time_sec,
        tracks_with_rating,
    )

    first_added = tracks_df["Date Added"].min()
    last_added = tracks_df["Date Added"].max()
    logging.debug("Date range: %s to %s", first_added, last_added)

    # Name and artist of first song added
    first_song_row = tracks_df.loc[tracks_df["Date Added"].idxmin()]
    first_song_name = create_artist_track_label(
        first_song_row["Artist"], first_song_row["Name"]
    )
    logging.debug("First song added: %s", first_song_name)

    # Name and artist of last song added
    last_song_row = tracks_df.loc[tracks_df["Date Added"].idxmax()]
    last_song_name = create_artist_track_label(
        last_song_row["Artist"], last_song_row["Name"]
    )
    logging.debug("Last song added: %s", last_song_name)

    # Calculate average playtime per day since first song added until today
    today = pd.Timestamp(datetime.now())
    days_since_first = (today - first_added).days or 1
    secs_since_first = (today - first_added).total_seconds()
    avg_playtime_since_first_sec = total_play_time_sec / days_since_first

    # Calculate average track length
    avg_track_length_sec = tracks_df["Total Time"].mean() / 1000  # assuming ms

    # Calculate average play count
    avg_play_count = tracks_df["Play Count"].fillna(0).mean()

    # Calculate average file size and total library size
    avg_file_size_bytes = tracks_df["Size"].mean()
    total_library_size_bytes = tracks_df["Size"].sum()

    logging.debug(
        "Library age: %d days (%.2f seconds total)",
        days_since_first,
        secs_since_first,
    )
    logging.debug(
        "Average calculations - track length: %.2f sec, play count: %.2f, file size: %.2f bytes",
        avg_track_length_sec,
        avg_play_count,
        avg_file_size_bytes,
    )
    logging.debug("Total library size: %.2f bytes", total_library_size_bytes)

    # Prepare table data
    stats = [
        ["Library Age", sec_to_human_readable(secs_since_first)],
        ["Total Library Size", bytes_to_human_readable(total_library_size_bytes)],
        ["Total Tracks", f"{total_tracks:,} tracks"],
        ["Rated Tracks", f"{tracks_with_rating:,} tracks"],
        ["Total Artists", f"{total_artists:,} artists"],
        ["Total Albums", f"{total_albums:,} albums"],
        ["Average Track Length", sec_to_human_readable(avg_track_length_sec)],
        ["Average Play Count", f"{avg_play_count:.1f} plays"],
        ["Average File Size", bytes_to_human_readable(avg_file_size_bytes)],
        ["First Song Added", first_added.strftime("%A, %B %d, %Y")],
        ["First Song", first_song_name],
        ["Last Song Added", last_added.strftime("%A, %B %d, %Y")],
        ["Last Song", last_song_name],
        ["Total Play Time", sec_to_human_readable(total_play_time_sec)],
        [
            "Average Play Time per Day",
            sec_to_human_readable(avg_playtime_since_first_sec),
        ],
    ]

    logging.debug("Generated %d statistics for the overview table", len(stats))
    logging.debug("Creating matplotlib figure and table")

    _, ax = plt.subplots(figsize=(8, 6))
    ax.axis("off")
    table = ax.table(
        cellText=stats,
        colLabels=["Statistic", "Value"],
        cellLoc="left",
        loc="center",
    )
    # Light blue shading for column label cells
    for (row, _), cell in table.get_celld().items():
        if row == 0:
            cell.set_facecolor("#e6f2ff")
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1, 1.5)

    title = "Library Overview"

    logging.debug("Saving plot to: %s.png", output_path)

    save_plot(title, output_path, ext="png", dpi=300)

    logging.debug("Library overview analysis completed successfully")

    return f"{output_path}.png"
