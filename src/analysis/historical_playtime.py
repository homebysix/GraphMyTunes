"""historical_playtime.py

For each track, multiply its play count by its duration to calculate
total listening time, then sum this for all tracks grouped by 'Date
Added' per quarter over time. Duration is assumed to be in milliseconds
(iTunes 'Total Time').
"""

from typing import Any, Dict

import matplotlib.pyplot as plt
import pandas as pd

from src.analysis._utils_ import ensure_columns, save_plot


def run(tracks_df: pd.DataFrame, params: Dict[str, Any], output_path: str) -> str:
    """This run() function is executed by the analysis engine."""

    ensure_columns(tracks_df, ["Date Added", "Play Count", "Total Time"])

    # Prepare data
    df = tracks_df.dropna(subset=["Date Added", "Play Count", "Total Time"]).copy()
    df["Date Added"] = pd.to_datetime(df["Date Added"], errors="coerce")
    df = df.dropna(subset=["Date Added"])

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

    # Group by quarter of 'Date Added' and sum total play time
    if isinstance(df["Date Added"].dtype, pd.DatetimeTZDtype):
        df["Quarter"] = df["Date Added"].dt.tz_localize(None).dt.to_period("Q")
    else:
        df["Quarter"] = df["Date Added"].dt.to_period("Q")
    window = df.groupby("Quarter")["Total Play Time (Hours)"].sum()

    # Set figure width dynamically based on number of columns
    plt.figure(figsize=(max(6, len(window) * 0.35), 6))

    # Plot the results
    window.plot(
        kind="bar",
        color=plt.get_cmap("tab10").colors,
        edgecolor="black",
    )
    plt.xlabel("Quarter")
    plt.ylabel("Total Listening Time (Hours)")
    title = "Total Listening Time by Quarter"
    save_plot(title, output_path, ext="png", dpi=300)

    return f"{output_path}.png"
