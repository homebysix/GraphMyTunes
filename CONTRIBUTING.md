# GraphMyTunes Contribution Guide

Thank you for your interest in contributing to GraphMyTunes! Your help is welcome, whether you're fixing bugs, adding features, improving documentation, or suggesting new analyses.

## Getting Started

1. **Fork the repository** on GitHub and clone your fork locally.

2. **Create a new branch** for your feature or bugfix:

    ```bash
    git checkout -b my-feature-branch
    ```

3. **Install dependencies** (preferably in a virtual environment):

    ```bash
    python3 -m virtualenv .venv
    source .venv/bin/activate
    .venv/bin/python3 -m pip install -r requirements.txt
    ```

## Code Quality & Style

This project uses several tools to maintain code quality and style. To set up these tools, install pre-commit (`brew install pre-commit`), then `cd` to your local clone of the GraphMyTunes repo and activate the pre-commit hooks (`pre-commit install`). Subsequent commits will be checked automatically for formatting and linting issues.

## Adding an Analysis

GraphMyTunes is designed to be simple to extend for those with Python and Matplotlib experience. Use the existing modules in `src/analysis/*.py` as your guide.

- Each analysis should be a new Python file in `src/analysis/`.
- Each module must define a `run(dataframe, params, output_path)` function.
- Use the `params` dictionary for user-specified configurations.
- Save output files (plots, CSVs, etc.) to the provided `output_path`.

## Running Tests

To ensure the functionality of the analysis functions, run the tests located in the `tests` directory:

```bash
.venv/bin/python3 -m unittest discover -vs tests
```

Please add or update tests for any new features or bug fixes.

## Submitting a Pull Request

1. **Push your branch** to your fork.
2. **Open a Pull Request** on GitHub.
3. **Describe your changes** clearly and reference any related issues.
4. Ensure all tests pass and code is linted before requesting review.

## Reporting Bugs & Suggestions

- Search [existing issues](https://github.com/homebysix/GraphMyTunes/issues?q=is%3Aissue) before opening a new one.
- When reporting a bug, include steps to reproduce, your OS, Python version, and any error messages.

---

Thank you for helping make GraphMyTunes better!
