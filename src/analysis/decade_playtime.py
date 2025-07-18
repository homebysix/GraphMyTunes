"""decade_playtime.py

Plot the total play time (play count x duration) for all tracks grouped by decade.
"""

from typing import Any, Dict

import matplotlib.pyplot as plt
import pandas as pd

from src.analysis._utils_ import ensure_columns, save_plot


def run(tracks_df: pd.DataFrame, params: Dict[str, Any], output_path: str) -> str:
    """This run() function is executed by the analysis engine."""

    ensure_columns(tracks_df, ["Year", "Play Count", "Total Time"])

    # Drop rows with missing or invalid years, play counts, or durations
    tracks_df = tracks_df.dropna(subset=["Year", "Play Count", "Total Time"])
    tracks_df = tracks_df[
        tracks_df["Year"].apply(lambda x: isinstance(x, (int, float)))
        & tracks_df["Play Count"].apply(lambda x: isinstance(x, (int, float)))
        & tracks_df["Total Time"].apply(lambda x: isinstance(x, (int, float)))
    ]

    # Calculate decade for each track
    tracks_df["Decade"] = (tracks_df["Year"] // 10 * 10).astype(int)

    # Calculate total play time per track (in seconds)
    # Convert Total Time from milliseconds to seconds before multiplying
    tracks_df["Play Time"] = tracks_df["Play Count"] * (tracks_df["Total Time"] / 1000)

    # Sum total play time per decade
    window = tracks_df.groupby("Decade")["Play Time"].sum().sort_index()

    # Add "s" to decade labels (e.g., 1990 -> "1990s")
    window.index = window.index.map(lambda d: f"{d}s")

    # Set figure width dynamically based on number of columns
    plt.figure(figsize=(max(8, len(window) * 0.35), 6))

    # Plot the results (convert seconds to hours for readability)
    (window / 3600).plot(
        kind="bar",
        color=plt.get_cmap("tab10").colors,
        edgecolor="black",
        legend=False,
    )
    plt.xlabel("Decade")
    plt.ylabel("Total Play Time (hours)")
    plt.xticks(rotation=45)
    title = "Total Play Time per Decade"
    save_plot(title, output_path, ext="png", dpi=300)

    return f"{output_path}.png"
