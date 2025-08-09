"""year_song_plays.py

Creates a timeline showing the most played song for each year,
displaying the track name, artist, and album information.
"""

import logging
import os
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd

from src.analysis._utils_ import (
    create_artist_track_label,
    ensure_columns,
    setup_analysis_logging,
)


def run(tracks_df: pd.DataFrame, params: dict[str, Any], output_path: str) -> str:
    """This run() function is executed by the analysis engine."""

    # Set up logging for this analysis process
    setup_analysis_logging(params.get("debug", False))
    logging.debug("Starting %s analysis", os.path.basename(__file__))

    # Ensure required columns exist
    ensure_columns(tracks_df, ["Year", "Name", "Artist", "Album", "Play Count"])

    # Drop rows with missing or invalid data
    df = tracks_df.dropna(
        subset=["Year", "Name", "Artist", "Album", "Play Count"]
    ).copy()
    df = df[df["Year"].apply(lambda x: isinstance(x, (int, float)))]
    df["Year"] = df["Year"].astype(int)

    # Convert Play Count to numeric, fill missing values with 0
    df["Play Count"] = (
        pd.to_numeric(df["Play Count"], errors="coerce").fillna(0).astype(int)
    )

    # Find the most played song for each year
    top_songs = (
        df.sort_values(["Year", "Play Count"], ascending=[True, False])
        .groupby("Year")
        .first()
        .reset_index()
    )

    # Sort by year for timeline
    top_songs = top_songs.sort_values("Year")

    # Create the timeline visualization
    fig, ax = plt.subplots(figsize=(10, max(4, len(top_songs) * 0.38)))

    # Create y-positions for each year (compressed spacing)
    y_positions = range(len(top_songs))

    # Draw vertical timeline spine
    ax.plot(
        [0, 0],
        [min(y_positions) - 0.3, max(y_positions) + 0.3],
        color="lightgray",
        linewidth=3,
        zorder=1,
    )

    # Add year labels and song information
    for i, (_, row) in enumerate(top_songs.iterrows()):
        y_pos = y_positions[i]

        # Alternate songs left and right
        is_left = i % 2 == 0

        # Year label centered on timeline (replacing the dot)
        ax.text(
            0,
            y_pos,
            str(int(row["Year"])),
            fontsize=11,
            fontweight="bold",
            ha="center",
            va="center",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="black"),
        )

        # Create formatted track label
        track_label = create_artist_track_label(row["Artist"], row["Name"], max_len=30)

        # Default values for left side labels
        x_text = 1.5
        ha_align = "left"
        arrow_start = 0.9
        arrow_end = 1.0

        # Opposite values for right side labels
        if is_left:
            x_text = -x_text
            ha_align = "right"
            arrow_start = -arrow_start
            arrow_end = -arrow_end

        # Add short arrow pointing from timeline to text
        ax.annotate(
            "",
            xy=(arrow_end, y_pos),
            xytext=(arrow_start, y_pos),
            arrowprops=dict(arrowstyle="-|>", color="gray", alpha=0.6, lw=1),
        )

        # Combine all song info into one text object
        album_text = f"{row['Album'][:25]}{'...' if len(row['Album']) > 25 else ''}"
        plays_text = f"({int(row['Play Count'])} plays)"

        combined_text = f"{track_label}\nAlbum: {album_text}\n{plays_text}"

        ax.text(
            x_text,
            y_pos,
            combined_text,
            fontsize=9,
            ha=ha_align,
            va="center",
            linespacing=1.3,
        )

    # Customize the plot
    ax.set_xlim(-2.5, 2.5)
    ax.set_ylim(min(y_positions) - 0.4, max(y_positions) + 0.38)
    ax.set_aspect("equal")

    # Remove axes and ticks
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(False)

    # Replicate save_plot functionality with 2% additional top space
    # Set the font properties for plots
    plt.rcParams["font.family"] = "Lato, Helvetica, Arial, sans-serif"
    plt.rcParams["font.size"] = 10
    plt.rcParams["axes.labelsize"] = 10
    plt.rcParams["axes.titlesize"] = 14
    plt.rcParams["axes.titleweight"] = "bold"

    # Configure matplotlib to handle LaTeX math text properly
    plt.rcParams["mathtext.default"] = "regular"
    plt.rcParams["mathtext.fontset"] = "dejavusans"

    # Set the plot title and style
    plt.suptitle(
        "Song of the Year Timeline (by Play Count)",
        fontsize=16,
        fontweight="bold",
        fontstyle="italic",
        color="black",
        ha="center",
    )

    # Keep layout tight, but leave extra space at the bottom for the footer
    # AND 2% additional space at the top
    plt.subplots_adjust(bottom=0.11)
    plt.tight_layout(rect=(0, 0.03, 1, 0.98))

    # Ensure grid lines are below the plot elements
    ax.set_axisbelow(True)

    # Remove spines for a cleaner look
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)

    # Add grid (simplified from save_plot)
    ax.grid(axis="y", linestyle="--", linewidth=0.5, alpha=0.5)

    # Add a footer with version info and GitHub link
    from src import __version__

    plt.gcf().text(
        0.99,
        0.01,
        f"GraphMyTunes v{__version__} ● https://github.com/homebysix/GraphMyTunes",
        fontsize=6,
        color="gray",
        ha="right",
        va="bottom",
        alpha=0.7,
    )

    # Save and close the plot
    plt.savefig(f"{output_path}.png", dpi=300)
    plt.close()

    return f"{output_path}.png"
