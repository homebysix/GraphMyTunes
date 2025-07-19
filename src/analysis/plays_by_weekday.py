"""plays_by_weekday.py

Graph the last played of tracks grouped by weekday. Uses the 'Play Date
UTC' field and converts to the specified time zone.
"""

from typing import Any, Dict

import matplotlib.pyplot as plt
import pandas as pd
import pytz

from src.analysis._utils_ import ensure_columns, save_plot, setup_analysis_logging


def run(tracks_df: pd.DataFrame, params: Dict[str, Any], output_path: str) -> str:
    """This run() function is executed by the analysis engine."""

    # Set up logging for this analysis process
    setup_analysis_logging(params.get("debug", False))

    # Ensure required columns exist
    ensure_columns(tracks_df, ["Play Date UTC"])

    # Get time zone from params or use default
    default_tz = "America/Los_Angeles"
    time_zone = params.get("time_zone", default_tz)
    try:
        tz = pytz.timezone(time_zone)
    except Exception:
        tz = pytz.timezone(default_tz)

    # Drop missing play dates and convert to datetime
    df = tracks_df.dropna(subset=["Play Date UTC"]).copy()
    df["Play Date UTC"] = pd.to_datetime(df["Play Date UTC"], errors="coerce", utc=True)
    df = df.dropna(subset=["Play Date UTC"])

    # Convert to local time zone
    df["Local Play Time"] = df["Play Date UTC"].dt.tz_convert(tz)

    # Extract weekday (0=Monday, 6=Sunday)
    df["Weekday"] = df["Local Play Time"].dt.weekday

    # Count plays by weekday across all years
    window = df.groupby("Weekday").size().reindex(range(7), fill_value=0)

    # Prepare labels for x-axis (weekday names)
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
    plt.ylabel("Tracks")
    plt.xticks(ticks=range(7), labels=weekday_labels, rotation=45)
    title = "Plays by Weekday"
    save_plot(title, output_path, ext="png", dpi=300)

    return f"{output_path}.png"
