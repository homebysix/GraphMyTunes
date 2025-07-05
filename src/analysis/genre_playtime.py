"""genre_playtime.py

Show the total play time (duration x play count) for all tracks in each
genre. Duration is assumed to be in milliseconds (iTunes 'Total Time').
"""

from typing import Any, Dict

import matplotlib.pyplot as plt
import pandas as pd

from src.analysis._utils_ import ensure_columns, save_plot


def run(tracks_df: pd.DataFrame, params: Dict[str, Any], output_path: str) -> str:
    """This run() function is executed by the analysis engine."""

    ensure_columns(tracks_df, ["Genre", "Play Count", "Total Time"])

    df = tracks_df.dropna(subset=["Genre", "Play Count", "Total Time"]).copy()

    # Convert Play Count and Total Time to numeric, fill missing values with 0
    df["Play Count"] = (
        pd.to_numeric(df["Play Count"], errors="coerce").fillna(0).astype(int)
    )
    df["Total Time"] = (
        pd.to_numeric(df["Total Time"], errors="coerce").fillna(0).astype(int)
    )

    # Calculate total play time per track in hours
    df["Total Play Time (Hours)"] = (df["Play Count"] * df["Total Time"]) / (
        1000 * 60 * 60
    )

    # Sum play time by genre
    window = (
        df.groupby("Genre")["Total Play Time (Hours)"]
        .sum()
        .sort_values(ascending=True)
        .tail(params["top"])
    )

    # Set figure height dynamically based on number of rows
    plt.figure(figsize=(6, max(2, len(window) * 0.35)))

    # Plot the data
    window.plot(
        kind="barh",
        color=plt.get_cmap("tab10").colors,
        edgecolor="black",
    )
    plt.ylabel("Genre")
    plt.xlabel("Total Play Time (Hours)")
    title = f"Top {params['top']} Genres by Total Play Time"
    save_plot(title, output_path, ext="png", dpi=300)

    return f"{output_path}.png"
