# ![GraphMyTunes](img/logo.png) <!-- omit in toc -->

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0) [![Python 3.13](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/downloads/release/python-3130/)

<!-- TODO: Badge for latest PyPI version, PyPI downloads, code coverage. -->

- [Overview](#overview)
- [Requirements](#requirements)
- [Quick Start](#quick-start)
    - [Step 1: Install Python and GraphMyTunes](#step-1-install-python-and-graphmytunes)
    - [Step 2: Export your music library to XML](#step-2-export-your-music-library-to-xml)
    - [Step 3: Run GraphMyTunes](#step-3-run-graphmytunes)
- [Featured Analyses](#featured-analyses)
- [Limitations and scope](#limitations-and-scope)
- [Support](#support)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

**GraphMyTunes builds insightful visualizations using the metadata in your Apple Music (formerly known as iTunes) library.** Its goal is to provide data to help you better understand your music listening and curation habits.

## Requirements

- **Apple Music app** for Mac or Windows
- **Python** (tested with 3.13, but probably works fine with 3.8 and higher)

## Quick Start

Follow these 3 steps to get started analyzing your music library.

### Step 1: Install Python and GraphMyTunes

1. [Download](https://www.python.org/downloads/) and install Python for Mac or Windows.
1. Use pip to install GraphMyTunes:

        pip install GraphMyTunes

### Step 2: Export your music library to XML

1. In the Apple Music app, choose **File > Library > Export Library**.
1. Save the XML file to a convenient location.

> [!TIP]
> **Tip:** I use a date-based filename like `2025-07-05.xml` so that I can save multiple snapshots of my library over time.

### Step 3: Run GraphMyTunes

1. Provide the path to the XML you just saved to GraphMyTunes for analysis.

        GraphMyTunes ~/Music/2025-07-05.xml

1. When processing is complete, view your graphs in the `output` folder.

## Featured Analyses

GraphMyTunes includes 40+ built-in ways to analyze your music collection, including but not limited to:

<div style="display: flex; flex-wrap: wrap; gap: 2em;">
<div style="flex: 1 1 300px; min-width: 250px;">

<p><strong>Top albums by total play time</strong><br />
<img src="img/album_playtime.png" alt="Top albums by total play time"></p>

<p><strong>Top artists by play count</strong><br />
<img src="img/artist_plays.png" alt="Top artists by play count"></p>

<p><strong>Top decades by play count</strong><br />
<img src="img/decade_plays.png" alt="Top decades by play count"></p>

</div>
<div style="flex: 1 1 300px; min-width: 250px;">

<p><strong>Top genres by total play time</strong><br />
<img src="img/genre_playtime.png" alt="Top genres by total play time"></p>

<p><strong>Plays by hour of day</strong><br />
<img src="img/plays_by_hour.png" alt="Plays by hour of day"></p>

<p><strong>Plays by day of week</strong><br />
<img src="img/plays_by_weekday.png" alt="Plays by day of week"></p>

</div>
</div>

## Limitations and scope

- At this time, GraphMyTunes development is focused around **Apple Music only**. There are likely other solutions that serve those with Spotify, Amazon, Pandora, or Last.fm libraries.

- GraphMyTunes is **limited by the metadata exported by the Music app.** Specifically, the exported XML does not include every date/time you played a track; it only includes the _most recent_ play date/time. Therefore, GraphMyTunes will not be able to surface some listening trends (for example, finding songs you used to listen to a lot but now listen to infrequently).

- GraphMyTunes **does not include single-metric metadata rankings that can easily be done in the Music app itself** (for example, listing the top tracks by play count). If you want these, go to the Music app's "Songs" view, adjust the view options to include the desired columns, and sort ascending or descending by that column. GraphMyTunes aims to provide ways to aggregate or group data in ways that the Music app cannot do.

## Support

Found a bug or have a suggestion? First check to see if somebody has already opened a similar [issue](https://github.com/homebysix/GraphMyTunes/issues?q=is%3Aissue) on GitHub. If not, feel free to [open one](https://github.com/homebysix/GraphMyTunes/issues/new?q=is%3Aissue).

## Contributing

Contributions are welcome! You may submit [pull requests](https://github.com/homebysix/GraphMyTunes/pulls) on GitHub. Please include a detailed description of the change being implemented, and consider including unit tests for any new features. See CONTRIBUTING.md for details.

## License

This project is licensed under the [Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0). See the LICENSE file for more details.
