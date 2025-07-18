"""library_overview.py

A few interesting stats about the music library, such as total number of tracks,
total number of artists, and total number of albums, total play time, first and
last songs added, and average playtime per day over the age of the library.
"""

from datetime import datetime
from typing import Any, Dict

import matplotlib.pyplot as plt
import pandas as pd

from src.analysis._utils_ import (
    bytes_to_human_readable,
    create_artist_track_label,
    ensure_columns,
    save_plot,
    sec_to_human_readable,
)


def run(tracks_df: pd.DataFrame, params: Dict[str, Any], output_path: str) -> str:
    """This run() function is executed by the analysis engine."""

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

    first_added = tracks_df["Date Added"].min()
    last_added = tracks_df["Date Added"].max()

    # Name and artist of first song added
    first_song_row = tracks_df.loc[tracks_df["Date Added"].idxmin()]
    first_song_name = create_artist_track_label(
        first_song_row["Artist"], first_song_row["Name"]
    )

    # Name and artist of last song added
    last_song_row = tracks_df.loc[tracks_df["Date Added"].idxmax()]
    last_song_name = create_artist_track_label(
        last_song_row["Artist"], last_song_row["Name"]
    )

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
    save_plot(title, output_path, ext="png", dpi=300)

    return f"{output_path}.png"
