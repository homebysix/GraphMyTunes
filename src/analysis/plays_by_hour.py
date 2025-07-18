"""plays_by_hour.py

Graph the last play date of tracks grouped by each of the 24 hours of
the day. Uses the 'Play Date UTC' field and converts to the specified
time zone.
"""

from typing import Any, Dict

import matplotlib.pyplot as plt
import pandas as pd
import pytz

from src.analysis._utils_ import ensure_columns, save_plot


def run(tracks_df: pd.DataFrame, params: Dict[str, Any], output_path: str) -> str:
    """This run() function is executed by the analysis engine."""

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
    df["Hour"] = df["Local Play Time"].dt.hour

    # Count plays by hour
    window = df["Hour"].value_counts().reindex(range(24), fill_value=0).sort_index()

    # Set figure width dynamically based on number of columns
    plt.figure(figsize=(max(8, len(window) * 0.35), 6))

    # Get hour format from params (default to 24-hour)
    hour_format = params.get("hour_format", "24")
    if hour_format == "24":
        hour_index = [str(h) for h in range(24)]
        rotation = 0
    else:
        hour_index = [f"{(h % 12 or 12)}{'am' if h < 12 else 'pm'}" for h in range(24)]
        rotation = 45

    # Plot the results
    window.plot(
        kind="bar",
        color=plt.get_cmap("tab10").colors,
        edgecolor="black",
    )
    plt.xlabel("Hour of Day")
    plt.ylabel("Tracks")
    plt.xticks(ticks=range(24), labels=hour_index, rotation=rotation)
    title = "Last Played by Hour of Day"
    save_plot(title, output_path, ext="png", dpi=300)

    return f"{output_path}.png"
