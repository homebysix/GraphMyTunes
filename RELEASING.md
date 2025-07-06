# Releasing a new version of GraphMyTunes

## Requirements

- Local clone of this repository
- Build tools (`venv/bin/python3 -m pip install build`)
- Twine (`venv/bin/python3 -m pip install twine`)
- Accounts on test.pypi.org and pypi.org

## Steps

1. Ensure the version in **pyproject.toml** has been updated.

1. Ensure the CHANGELOG.md has been updated and reflects actual release date.

1. Merge dev branch to main branch.

1. Run unit tests and fix any errors:

        venv/bin/python3 -m unittest discover -vs tests

1. Build a new distribution package:

        rm -rf dist/* build/ src/*.egg-info
        venv/bin/python3 -m build

1. Upload package to test.pypi.org:

        venv/bin/python3 -m twine upload --repository testpypi dist/*

1. View resulting [project on test.pypi.org](https://test.pypi.org/project/GraphMyTunes/) and make sure it looks good.

1. Install test GraphMyTunes from test.pypi.org:

        venv/bin/python3 -m pip install --upgrade -i https://test.pypi.org/simple/ GraphMyTunes

1. Perform manual tests (a GitHub Actions workflow also performs these tests):

        venv/bin/graphmytunes --version
        venv/bin/graphmytunes --help
        venv/bin/graphmytunes /path/to/itunes.xml

1. Upload package to pypi.org:

        venv/bin/python3 -m twine upload dist/*

1. View resulting [project on pypi.org](https://pypi.org/project/GraphMyTunes/) and make sure it looks good.

1. Install production GraphMyTunes:

        venv/bin/python3 -m pip install --upgrade GraphMyTunes

1. Create new [release](https://github.com/homebysix/GraphMyTunes/releases) on GitHub. Add notes from change log.

1. Announce to relevant channels, if desired.
