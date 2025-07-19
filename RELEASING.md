# Releasing a new version of GraphMyTunes

New versions of GraphMyTunes can be published as follows.

## Step 1: Local preparation

1. Ensure the CHANGELOG.md has been updated with version-specific release notes in [keep-a-changelog format](https://keepachangelog.com/).

1. Run pre-commit hooks and unit tests and fix any errors:

        pre-commit run --all-files
        .venv/bin/python -m unittest discover -vs tests

1. Build a new distribution package:

        rm -rf dist/* build/ src/*.egg-info
        .venv/bin/python -m build

1. Install locally and verify success:

        .venv/bin/python -m pip install -e . --force-reinstall
        .venv/bin/graphmytunes --version

## Step 2: Publish to TestPyPI

1. From the dev branch, create and push a new tag:

        ./scripts/release.py 1.2.3  # adjust to match actual version

1. GitHub Actions will automatically publish to TestPyPI and post a comment with verification instructions.

1. Install from TestPyPI:

        .venv/bin/python -m pip install --upgrade -i https://test.pypi.org/simple/ GraphMyTunes==1.2.3

1. Perform manual tests:

        .venv/bin/graphmytunes --version
        .venv/bin/graphmytunes --help
        .venv/bin/graphmytunes /path/to/itunes.xml

## Step 3: Publish to PyPI and GitHub

1. From the dev branch, create and push a new tag for the final release:

        ./scripts/release.py 1.2.3  # adjust to match actual version

1. GitHub Actions will automatically publish to PyPI and post a comment with next steps.

1. After successful PyPI publication, GitHub will automatically create a GitHub release with changelog notes and post a success notification.

1. Confirm the package is available on [PyPI](https://pypi.org/project/GraphMyTunes/):

        .venv/bin/python -m pip install --upgrade GraphMyTunes

1. Confirm the [latest GitHub release](https://github.com/homebysix/GraphMyTunes/releases/latest) is correct.

1. Announce to relevant channels, if desired.
