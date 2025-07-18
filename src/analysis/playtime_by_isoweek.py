"""playtime_by_isoweek.py

Graph the total play time (Play Count * Total Time) grouped by ISO week
number. Uses the 'Play Date UTC' field and converts to the specified
time zone.
"""

from typing import Any, Dict

import matplotlib.pyplot as plt
import pandas as pd
import pytz

from src.analysis._utils_ import ensure_columns, save_plot


def run(tracks_df: pd.DataFrame, params: Dict[str, Any], output_path: str) -> str:
    """This run() function is executed by the analysis engine."""

    ensure_columns(tracks_df, ["Play Date UTC", "Play Count", "Total Time"])

    # Get time zone from params or use default
    default_tz = "America/Los_Angeles"
    time_zone = params.get("time_zone", default_tz)
    try:
        tz = pytz.timezone(time_zone)
    except Exception:
        tz = pytz.timezone(default_tz)

    # Drop missing play dates and convert to datetime
    df = tracks_df.dropna(subset=["Play Date UTC", "Play Count", "Total Time"]).copy()
    df["Play Date UTC"] = pd.to_datetime(df["Play Date UTC"], errors="coerce", utc=True)
    df = df.dropna(subset=["Play Date UTC"])

    # Convert to local time zone
    df["Local Play Time"] = df["Play Date UTC"].dt.tz_convert(tz)

    # Extract ISO week number
    df["ISO Week"] = df["Local Play Time"].dt.isocalendar().week

    # Calculate play time (Play Count * Total Time)
    # Assume "Total Time" is in milliseconds; convert to hours for plotting
    df["Play Time (hours)"] = df["Play Count"] * df["Total Time"] / (1000 * 60 * 60)

    # Sum play time by ISO week (across all years)
    window = df.groupby("ISO Week")["Play Time (hours)"].sum().sort_index()

    # Prepare labels for x-axis
    week_labels = [f"W{week:02d}" for week in window.index]

    # Set figure width dynamically based on number of columns
    plt.figure(figsize=(max(8, len(window) * 0.35), 6))

    # Plot the results
    window.plot(
        kind="bar",
        color=plt.get_cmap("tab10").colors,
        edgecolor="black",
    )
    plt.xlabel("ISO Week")
    plt.ylabel("Play Time (hours)")
    plt.xticks(ticks=range(len(week_labels)), labels=week_labels, rotation=90)
    title = "Total Play Time by ISO Week Number"
    save_plot(title, output_path, ext="png", dpi=300)

    return f"{output_path}.png"
