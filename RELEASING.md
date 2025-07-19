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

1. Create and push a new tag using the release script:

        ./scripts/release.py 1.2.3  # adjust to match actual version

   This script will:
   - Update the version in `pyproject.toml`
   - Commit the version change
   - Create and push a git tag (`v1.2.3`)
   - Trigger the automated CI/CD workflow

1. GitHub Actions will:
    - Publish to TestPyPI
    - Post a comment with next steps

1. Install from TestPyPI and test:

        .venv/bin/python -m pip install --upgrade -i https://test.pypi.org/simple/ GraphMyTunes==1.2.3
        .venv/bin/graphmytunes --version
        .venv/bin/graphmytunes --help
        .venv/bin/graphmytunes /path/to/itunes.xml

## Step 3: Publish to PyPI and GitHub

1. Go to [GitHub Actions](https://github.com/homebysix/GraphMyTunes/actions/workflows/publish.yml) and manually trigger the workflow:
   - Click "Run workflow"
   - Select the tag you want to publish (e.g., `v1.2.3`)
   - Set "Target repository" to `pypi`
   - Click "Run workflow"

1. GitHub Actions will:
   - Publish to PyPI
   - Create a GitHub release with changelog notes
   - Post a success notification

1. Confirm the package is available on [PyPI](https://pypi.org/project/GraphMyTunes/):

        .venv/bin/python -m pip install --upgrade GraphMyTunes

1. Confirm the [latest GitHub release](https://github.com/homebysix/GraphMyTunes/releases/latest) is correct.

1. Announce to relevant channels, if desired.
