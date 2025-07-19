"""album_wordcloud.py

Generate a word cloud visualization of all the words in album names in the library.
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
    ensure_columns(tracks_df, ["Album"])

    # Get all album names and drop missing values
    album_names = tracks_df["Album"].dropna().astype(str)

    # Add custom album-specific stop words if needed
    custom_stopwords = STOPWORDS.copy()
    custom_stopwords.update(
        {
            "album",
            "greatest",
            "hits",
        }
    )

    # Create the word cloud
    wordcloud = create_wordcloud(album_names, custom_stopwords, params)

    # Create the plot
    plt.figure(figsize=(12, 6))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")

    title = "Album Names Word Cloud"
    save_plot(title, output_path, ext="png", dpi=300)

    return f"{output_path}.png"
