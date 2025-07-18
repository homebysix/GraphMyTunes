"""playtime_by_weekday.py

Graph the total play time of tracks grouped by weekday. Uses the 'Play
Date UTC', 'Play Count', and 'Total Time' fields and converts to the
specified time zone.
"""

from typing import Any, Dict

import matplotlib.pyplot as plt
import pandas as pd
import pytz

from src.analysis._utils_ import ensure_columns, save_plot


def run(tracks_df: pd.DataFrame, params: Dict[str, Any], output_path: str) -> str:
    """This run() function is executed by the analysis engine."""

    ensure_columns(tracks_df, ["Play Date UTC", "Play Count", "Total Time"])

    default_tz = "America/Los_Angeles"
    time_zone = params.get("time_zone", default_tz)
    try:
        tz = pytz.timezone(time_zone)
    except Exception:
        tz = pytz.timezone(default_tz)

    df = tracks_df.dropna(subset=["Play Date UTC", "Play Count", "Total Time"]).copy()
    df["Play Date UTC"] = pd.to_datetime(df["Play Date UTC"], errors="coerce", utc=True)
    df = df.dropna(subset=["Play Date UTC"])

    df["Local Play Time"] = df["Play Date UTC"].dt.tz_convert(tz)
    df["Weekday"] = df["Local Play Time"].dt.weekday

    # Calculate play time in hours
    df["Play Time (hrs)"] = (df["Play Count"] * df["Total Time"]) / (1000 * 60 * 60)

    # Sum play time by weekday
    window = (
        df.groupby("Weekday")["Play Time (hrs)"].sum().reindex(range(7), fill_value=0)
    )

    weekday_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    # Set figure width dynamically based on number of columns
    plt.figure(figsize=(max(8, len(window) * 0.35), 6))

    # Plot the results
    window.plot(
        kind="bar",
        color=plt.get_cmap("tab10").colors,
        edgecolor="black",
    )
    plt.xlabel("Weekday")
    plt.ylabel("Play Time (hours)")
    plt.xticks(ticks=range(7), labels=weekday_labels, rotation=45)
    title = "Total Play Time by Weekday"
    save_plot(title, output_path, ext="png", dpi=300)

    return f"{output_path}.png"
