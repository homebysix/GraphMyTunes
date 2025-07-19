"""artist_wordcloud.py

Generate a word cloud visualization of all the words in artist names in the library.
Common words like "the", "and", "a", etc. are filtered out to highlight more
meaningful words.
"""

from typing import Any, Dict

import matplotlib.pyplot as plt
import pandas as pd
from wordcloud import STOPWORDS

from src.analysis._utils_ import (
    create_wordcloud,
    ensure_columns,
    save_plot,
    setup_analysis_logging,
)


def run(tracks_df: pd.DataFrame, params: Dict[str, Any], output_path: str) -> str:
    """This run() function is executed by the analysis engine."""

    # Set up logging for this analysis process
    setup_analysis_logging(params.get("debug", False))

    # Ensure required columns exist
    ensure_columns(tracks_df, ["Artist"])

    # Get all artist names and drop missing values
    artist_names = tracks_df["Artist"].dropna().astype(str)

    # Add custom artist-specific stop words if needed
    custom_stopwords = STOPWORDS.copy()
    custom_stopwords.update({})

    # Create the word cloud
    wordcloud = create_wordcloud(artist_names, custom_stopwords, params)

    # Create the plot
    plt.figure(figsize=(12, 6))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")

    title = "Artist Names Word Cloud"
    save_plot(title, output_path, ext="png", dpi=300)

    return f"{output_path}.png"
