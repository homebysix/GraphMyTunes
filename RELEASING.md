# Releasing a new version of GraphMyTunes

## Requirements

- Local clone of this repository
- Build tools (`venv/bin/python3 -m pip install build`)
- Twine (`venv/bin/python3 -m pip install twine`)
- Accounts on test.pypi.org and pypi.org

## Steps

### Local preparation

1. Ensure the CHANGELOG.md has been updated and reflects actual release date.

1. Run unit tests and pre-commit hooks and fix any errors:

        venv/bin/python3 -m unittest discover -vs tests
        pre-commit run --all-files

1. Build a new distribution package:

        rm -rf dist/* build/ src/*.egg-info
        venv/bin/python3 -m build

1. Install locally and verify success:

        venv/bin/python -m pip install -e . --force-reinstall
        venv/bin/graphmytunes --version

### Publish test

1. From the dev branch, create and push a new tag for release candidate:

        ./scripts/release.py 1.2.3rc1  # adjust to match actual rc version

1. Verify that the new version publishes successfully to [test.pypi.org](https://test.pypi.org/project/GraphMyTunes/).

1. Install from test.pypi.org:

        venv/bin/python3 -m pip install --upgrade -i https://test.pypi.org/simple/ GraphMyTunes

1. Perform manual tests (a GitHub Actions workflow also performs these tests):

        venv/bin/graphmytunes --version
        venv/bin/graphmytunes --help
        venv/bin/graphmytunes /path/to/itunes.xml

### Publish final release

1. From the dev branch, create and push a new tag for release candidate:

        ./scripts/release.py 1.2.3  # adjust to match actual final version

1. Verify that the new version publishes successfully to [pypi.org](https://pypi.org/project/GraphMyTunes/).

1. Install from pypi.org:

        venv/bin/python3 -m pip install --upgrade GraphMyTunes

1. Perform manual tests (a GitHub Actions workflow also performs these tests):

        venv/bin/graphmytunes --version
        venv/bin/graphmytunes --help
        venv/bin/graphmytunes /path/to/itunes.xml

1. Create new [release](https://github.com/homebysix/GraphMyTunes/releases) on GitHub. Add notes from change log.

1. Announce to relevant channels, if desired.
