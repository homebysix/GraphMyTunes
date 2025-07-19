"""_utils_.py

Utility functions for GraphMyTunes analysis modules.
"""

import logging

import matplotlib

# Use the 'Agg' backend for non-GUI rendering
matplotlib.use("Agg")
import os
import re
from typing import Any, Dict, List

# flake8: noqa: E402
import matplotlib.pyplot as plt
import pandas as pd
from wordcloud import WordCloud

from src import __version__


def setup_analysis_logging(debug: bool = False) -> None:
    """Set up logging configuration for analysis modules.

    This is needed because analysis modules run in separate processes
    and don't inherit the main process's logging configuration.
    """
    if debug and not logging.getLogger().handlers:
        # Only configure logging if it hasn't been configured yet in this process
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s [%(levelname)s] %(message)s {%(filename)s:%(lineno)d}",
        )

    # Always suppress verbose matplotlib font debugging
    logging.getLogger("matplotlib.font_manager").setLevel(logging.WARNING)


def ensure_columns(df: pd.DataFrame, columns: List[str]) -> None:
    """Ensure the DataFrame contains the specified columns."""
    missing = [col for col in columns if col not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")


def rating_to_stars(rating: pd.Series) -> pd.Series:
    """Convert iTunes ratings (0-100 scale) to 0-5 stars."""
    rating = (rating.fillna(0) / 20).round().astype(int)
    return rating.clip(lower=0, upper=5)


def trim_label(label: str, max_len: int = 32) -> str:
    """Trim a label to a maximum length, appending an ellipsis if it exceeds
    the limit."""
    return label if len(label) <= max_len else label[:max_len].strip() + "…"


def create_artist_track_label(artist: str, title: str, max_len: int = 32) -> str:
    """Create a formatted label with artist name followed by quoted track title.

    Args:
        artist: The artist name
        title: The track title

    Returns:
        A formatted string like 'Artist Name: "Track Title"'
    """
    return f"{artist}: “{trim_label(title, max_len)}”"


def create_artist_album_label(artist: str, album: str, max_len: int = 32) -> str:
    """Create a formatted label with artist name followed by italicized album name, separated by a colon.

    Args:
        artist: The artist name
        album: The album name
        max_len: Maximum length for the album name before trimming

    Returns:
        A formatted string like "Artist Name: Album Name" with proper LaTeX escaping
    """
    trimmed_album = trim_label(album, max_len)

    # Simple approach: Only use LaTeX for albums with safe characters
    # This avoids the complexity of escaping while still providing italics where possible
    unsafe_chars = set("#&%$_^~\\{}|<>")

    if any(char in unsafe_chars for char in trimmed_album):
        # For albums with problematic characters, use simple formatting
        return f"{artist}: {trimmed_album}"
    else:
        # For safe albums, use LaTeX italics
        # Replace spaces with LaTeX spacing
        safe_album = trimmed_album.replace(" ", "\\ ")
        return f"{artist}: $\\mathit{{{safe_album}}}$"


def get_numeric_axes(ax: plt.Axes) -> str:
    """Return "x" if x-axis is numeric, "y" otherwise."""

    def is_numeric(tick_labels: List[plt.Text]) -> bool:
        """Check if the first tick label of a given axis is numeric."""
        if not tick_labels:
            return False
        try:
            float(tick_labels[0].get_text())
            return True
        except ValueError:
            return False

    if ax.get_yticklabels() and is_numeric(ax.get_yticklabels()):
        if ax.get_xticklabels() and is_numeric(ax.get_xticklabels()):
            # Both axes are numeric, prefer x-axis
            return "y"
    if ax.get_xticklabels() and is_numeric(ax.get_xticklabels()):
        # Only x-axis is numeric
        return "x"

    # Neither axis is numeric, default to y-axis
    return "y"


def save_plot(title: str, output_path: str, ext: str = "png", dpi: int = 300) -> None:
    """Save the current plot to a file with the specified extension and dpi,
    with a footer."""

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
        title,
        fontsize=16,
        fontweight="bold",
        fontstyle="italic",
        color="black",
        ha="center",
    )

    # Keep layout tight, but leave extra space at the bottom for the footer
    plt.subplots_adjust(bottom=0.11)
    plt.tight_layout(rect=(0, 0.03, 1, 1))

    # Ensure grid lines are below the plot elements
    ax = plt.gca()
    ax.set_axisbelow(True)

    # Remove spines for a cleaner look
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)

    # Print text of first tick label of x axis
    ax.grid(axis=get_numeric_axes(ax), linestyle="--", linewidth=0.5, alpha=0.5)

    # Add a footer with version info and GitHub link
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
    plt.savefig(f"{output_path}.{ext}", dpi=dpi)
    plt.close()


def get_today_matching_tz(date_series: pd.Series) -> pd.Timestamp:
    """Return 'today' as a pd.Timestamp, tz-aware if date_series is tz-aware,
    else naive."""
    if isinstance(date_series.dtype, pd.DatetimeTZDtype):
        tz = date_series.dt.tz
        return pd.Timestamp.now(tz=tz).normalize()
    else:
        return pd.Timestamp.now().normalize()


def sec_to_human_readable(secs: int) -> str:
    """Convert seconds to a human-readable format.
    Format: {YEAR}y {WEEK}w {DAY}d {HOUR}h {MINUTE}m {SECOND}s
    """
    if secs < 0:
        return "0s"

    years, remainder = divmod(secs, 31536000)  # 60 * 60 * 24 * 365
    days, remainder = divmod(remainder, 86400)  # 60 * 60 * 24
    hours, remainder = divmod(remainder, 3600)  # 60 * 60
    minutes, seconds = divmod(remainder, 60)

    parts = []
    units = [
        ("y", years),
        ("d", days),
        ("h", hours),
        ("m", minutes),
        ("s", seconds),
    ]
    parts = [f"{int(value)}{unit}" for unit, value in units if value]
    if not parts:
        parts.append("0s")

    return " ".join(parts)


def bytes_to_human_readable(bytes_val):
    """Convert bytes to a human-readable format."""
    if bytes_val >= 1024**3:  # GB
        return f"{bytes_val / (1024**3):.1f} GB"
    elif bytes_val >= 1024**2:  # MB
        return f"{bytes_val / (1024**2):.1f} MB"
    elif bytes_val >= 1024:  # KB
        return f"{bytes_val / 1024:.1f} KB"
    else:
        return f"{bytes_val:.0f} bytes"


def create_wordcloud(
    text: pd.Series, stopwords: set, params: Dict[str, Any]
) -> WordCloud:
    """Create a WordCloud object from the given text and stopwords."""

    # Remove duplicates
    unique_titles = text.drop_duplicates()

    # Combine all titles into one text string
    all_titles_text = " ".join(unique_titles)

    # Clean the text: remove extra whitespace and convert to lowercase
    all_titles_text = re.sub(r"\s+", " ", all_titles_text.lower().strip())

    # Create the word cloud
    max_words = params.get("max_words", 200)
    wordcloud = WordCloud(
        width=1200,
        height=600,
        background_color="white",
        stopwords=stopwords,
        max_words=max_words,
        colormap="plasma",
        relative_scaling=0.5,
        min_font_size=10,
        max_font_size=100,
        prefer_horizontal=0.9,
        collocations=False,  # Don't group words together
        normalize_plurals=False,  # Keep plurals as separate words
    ).generate(all_titles_text)

    return wordcloud
