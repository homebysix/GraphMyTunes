"""yearly_songs_by_playtime.py

Output a table containing the top N songs by total play time (Play Count
x Total Time) for every Year represented by tracks in the library, and
the total play time. Skips years with no songs associated.
"""

from typing import Any, Dict

import pandas as pd

from src.analysis._utils_ import ensure_columns, sec_to_human_readable


def run(tracks_df: pd.DataFrame, params: Dict[str, Any], output_path: str) -> str:
    """This run() function is executed by the analysis engine."""

    ensure_columns(tracks_df, ["Year", "Name", "Play Count", "Total Time"])

    # Drop rows with missing or invalid years, play counts, names, artists, albums, or total time
    df = tracks_df.dropna(
        subset=["Year", "Name", "Play Count", "Artist", "Album", "Total Time"]
    ).copy()
    df = df[df["Year"].apply(lambda x: isinstance(x, (int, float)))]
    df["Year"] = df["Year"].astype(int)

    # Convert Play Count and Total Time to numeric, fill missing values with 0
    df["Play Count"] = (
        pd.to_numeric(df["Play Count"], errors="coerce").fillna(0).astype(int)
    )
    df["Total Time"] = (
        pd.to_numeric(df["Total Time"], errors="coerce").fillna(0).astype(int)
    )

    # Calculate total play time (Play Count x Total Time), converting ms to seconds
    df["Total Play Time (Sec)"] = (df["Play Count"] * df["Total Time"] // 1000).astype(
        int
    )

    # Convert total play time to human-readable format using sec_to_human_readable()
    df["Total Play Time (Readable)"] = df["Total Play Time (Sec)"].apply(
        sec_to_human_readable
    )

    # Find the top N songs by play time for each year, including Artist and Album
    top_songs = (
        df.sort_values(["Year", "Total Play Time (Sec)"], ascending=[True, False])
        .groupby("Year")
        .head(params["top"])
        .loc[
            :,
            [
                "Year",
                "Name",
                "Artist",
                "Album",
                "Total Play Time (Sec)",
                "Total Play Time (Readable)",
            ],
        ]
    )

    # If more than one song per year is requested, add a rank column
    if params["top"] > 1:
        top_songs.insert(1, "Rank", top_songs.groupby("Year").cumcount() + 1)

    # Save as CSV table
    top_songs.to_csv(f"{output_path}.csv", index=False)

    return f"{output_path}.csv"
