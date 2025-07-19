"""playtime_by_month.py

Graph the total play time grouped by month. Uses the 'Play Date UTC'
field and converts to the specified time zone. Play time is calculated
as 'Play Count' * 'Total Time' (in milliseconds).
"""

import logging
import os
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
import pytz

from src.analysis._utils_ import ensure_columns, save_plot, setup_analysis_logging


def run(tracks_df: pd.DataFrame, params: dict[str, Any], output_path: str) -> str:
    """This run() function is executed by the analysis engine."""

    # Set up logging for this analysis process
    setup_analysis_logging(params.get("debug", False))
    logging.debug("Starting %s analysis", os.path.basename(__file__))

    # Ensure required columns exist
    ensure_columns(tracks_df, ["Play Date UTC", "Play Count", "Total Time"])

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

    # Extract month (1-12)
    df["Month"] = df["Local Play Time"].dt.month

    # Calculate play time per track (in hours)
    df["Play Time (hours)"] = (
        df["Play Count"].fillna(0) * df["Total Time"].fillna(0)
    ) / (1000 * 60 * 60)

    # Sum play time by month across all years
    window = (
        df.groupby("Month")["Play Time (hours)"]
        .sum()
        .reindex(range(1, 13), fill_value=0)
    )

    # Prepare labels for x-axis (month names)
    month_labels = [
        pd.Timestamp(month=m, day=1, year=2000).strftime("%B") for m in window.index
    ]

    # Set figure width dynamically based on number of columns
    plt.figure(figsize=(max(8, len(window) * 0.35), 6))

    # Plot the results
    window.plot(
        kind="bar",
        color=plt.get_cmap("tab10").colors,
        edgecolor="black",
    )
    plt.xlabel("Month")
    plt.ylabel("Play Time (hours)")
    plt.xticks(ticks=range(12), labels=month_labels, rotation=45)
    title = "Total Play Time by Month"
    save_plot(title, output_path, ext="png", dpi=300)

    return f"{output_path}.png"
