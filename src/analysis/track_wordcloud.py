"""track_wordcloud.py

Generate a word cloud visualization of all the words in song titles in the library.
Common words like "the", "and", "a", etc. are filtered out to highlight more
meaningful words.
"""

import logging
import os
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
from wordcloud import STOPWORDS

from src.analysis._utils_ import (
    create_wordcloud,
    ensure_columns,
    save_plot,
    setup_analysis_logging,
)


def run(tracks_df: pd.DataFrame, params: dict[str, Any], output_path: str) -> str:
    """This run() function is executed by the analysis engine."""

    # Set up logging for this analysis process
    setup_analysis_logging(params.get("debug", False))
    logging.debug("Starting %s analysis", os.path.basename(__file__))

    # Ensure required columns exist
    ensure_columns(tracks_df, ["Name"])

    # Get all song titles and drop missing values
    song_titles = tracks_df["Name"].dropna().astype(str)

    # Add custom track-specific stop words if needed
    custom_stopwords = STOPWORDS.copy()
    custom_stopwords.update(
        {
            "demo",
            "edit",
            "feat",
            "live",
            "mix",
            "radio",
            "remix",
            "version",
        }
    )

    # Create the word cloud
    wordcloud = create_wordcloud(song_titles, custom_stopwords, params)

    # Create the plot
    plt.figure(figsize=(12, 6))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")

    title = "Track Titles Word Cloud"
    save_plot(title, output_path, ext="png", dpi=300)

    return f"{output_path}.png"
