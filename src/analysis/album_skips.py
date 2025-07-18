"""album_skips.py

Show the total skip count for all tracks in each album.
"""

from typing import Any, Dict

import matplotlib.pyplot as plt
import pandas as pd

from src.analysis._utils_ import ensure_columns, save_plot, trim_label


def run(tracks_df: pd.DataFrame, params: Dict[str, Any], output_path: str) -> str:
    """This run() function is executed by the analysis engine."""

    ensure_columns(tracks_df, ["Album", "Skip Count"])

    df = tracks_df.dropna(subset=["Album", "Skip Count"]).copy()

    # Convert Skip Count to numeric, fill missing values with 0
    df["Skip Count"] = (
        pd.to_numeric(df["Skip Count"], errors="coerce").fillna(0).astype(int)
    )

    # Trim long names
    df["Album (Trimmed)"] = df["Album"].apply(trim_label)

    # Sum skip count by trimmed album and get top N
    window = (
        df.groupby("Album (Trimmed)")["Skip Count"]
        .sum()
        .sort_values(ascending=True)
        .tail(params["top"])
    )

    # Set figure height dynamically based on number of rows
    plt.figure(figsize=(8, max(2, len(window) * 0.35)))

    # Plot the data
    window.plot(
        kind="barh",
        color=plt.get_cmap("tab10").colors,
        edgecolor="black",
    )
    plt.ylabel("Album")
    plt.xlabel("Total Skip Count")
    title = f"Top {params['top']} Albums by Skip Count"
    save_plot(title, output_path, ext="png", dpi=300)

    return f"{output_path}.png"
