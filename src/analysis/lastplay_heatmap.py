"""lastplay_heatmap.py

Create a 2D heatmap visualization showing listening patterns by day-of-week
vs. hour-of-day based on the "Last Played" timestamps.
"""

from typing import Any, Dict

import matplotlib.pyplot as plt
import pandas as pd
import pytz

from src.analysis._utils_ import ensure_columns, save_plot


def run(tracks_df: pd.DataFrame, params: Dict[str, Any], output_path: str) -> str:
    """This run() function is executed by the analysis engine."""

    # Ensure we have the Play Date UTC column
    ensure_columns(tracks_df, ["Play Date UTC"])

    # Get time zone from params or use default
    default_tz = "America/Los_Angeles"
    time_zone = params.get("time_zone", default_tz)
    try:
        tz = pytz.timezone(time_zone)
    except Exception:
        tz = pytz.timezone(default_tz)

    df = tracks_df.dropna(subset=["Play Date UTC"]).copy()

    # Check if we have enough data
    if len(df) == 0:
        raise ValueError("No tracks with Play Date UTC timestamps found")

    # Convert play date timestamp to datetime and convert to local time
    df["Play DateTime"] = pd.to_datetime(df["Play Date UTC"], errors="coerce", utc=True)
    df = df.dropna(subset=["Play DateTime"])

    if len(df) == 0:
        raise ValueError("No tracks with valid Play Date UTC timestamps found")

    # Convert UTC timestamps to local time using pytz (same as plays_by_hour)
    df["Play DateTime"] = df["Play DateTime"].dt.tz_convert(tz)

    # Convert to timezone-naive (remove timezone info but keep local time)
    df["Play DateTime"] = df["Play DateTime"].dt.tz_localize(None)

    # Remove duplicate timestamps - keep only first occurrence of each exact timestamp
    original_count = len(df)
    df = df.drop_duplicates(subset=["Play DateTime"], keep="first")
    duplicate_count = original_count - len(df)

    if duplicate_count > 0:
        print(
            f"Removed {duplicate_count} tracks with duplicate timestamps ({duplicate_count/original_count*100:.1f}%)"
        )

    # Extract day of week and hour
    df["Day of Week"] = df["Play DateTime"].dt.day_name()
    df["Hour"] = df["Play DateTime"].dt.hour

    # Create a pivot table for the heatmap
    # Count the number of plays for each day-hour combination
    heatmap_data = (
        df.groupby(["Day of Week", "Hour"]).size().reset_index(name="Play Count")
    )

    # Create a complete grid with all day-hour combinations
    days_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    hours_range = list(range(24))

    # Create a pivot table with the correct ordering
    pivot_data = heatmap_data.pivot(
        index="Day of Week", columns="Hour", values="Play Count"
    )
    pivot_data = pivot_data.reindex(index=days_order, columns=hours_range, fill_value=0)

    # Create the heatmap
    fig, ax = plt.subplots(figsize=(12, 6))

    # Create the heatmap using imshow for better control
    im = ax.imshow(
        pivot_data.values, cmap="YlOrRd", aspect="auto", interpolation="nearest"
    )

    # Set the ticks and labels
    ax.set_xticks(range(24))
    ax.set_xticklabels([f"{hour:02d}:00" for hour in range(24)])
    ax.set_yticks(range(7))
    ax.set_yticklabels(days_order)

    # Rotate x-axis labels for better readability
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")

    # Add labels
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Day of Week")

    # Add colorbar
    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label("Number of Plays", rotation=270, labelpad=20)

    # Improve layout
    plt.tight_layout()

    # Add some statistics as text
    peak_hour = pivot_data.sum(axis=0).idxmax()
    peak_day = pivot_data.sum(axis=1).idxmax()

    stats_text = f"Peak listening: {peak_day} at {peak_hour:02d}:00"
    ax.text(
        0.02,
        0.98,
        stats_text,
        transform=ax.transAxes,
        fontsize=10,
        verticalalignment="top",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
    )

    title = "Listening Patterns: Day of Week vs. Hour of Day Heatmap"
    save_plot(title, output_path, ext="png", dpi=300)

    return f"{output_path}.png"
