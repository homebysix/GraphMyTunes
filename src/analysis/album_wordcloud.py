"""album_wordcloud.py

Generate a word cloud visualization of all the words in album names in the library.
Common words like "the", "and", "a", etc. are filtered out to highlight more
meaningful words.
"""

from typing import Any, Dict

import matplotlib.pyplot as plt
import pandas as pd
from wordcloud import STOPWORDS

from src.analysis._utils_ import create_wordcloud, ensure_columns, save_plot


def run(tracks_df: pd.DataFrame, params: Dict[str, Any], output_path: str) -> str:
    """This run() function is executed by the analysis engine."""

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
