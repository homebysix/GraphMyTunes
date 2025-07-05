import importlib
import os
import plistlib
import tempfile
import unittest
from glob import glob

import pandas as pd

# List of modules that produce CSV output instead of PNG images
CSV_MODULES = ("yearly_songs_by_plays", "yearly_songs_by_playtime")

# Load sample data from plist
with open(os.path.join(os.path.dirname(__file__), "data", "sample.xml"), "rb") as f:
    TEST_DATA = plistlib.load(f)


class AnalysisTestBase(unittest.TestCase):
    """Base class for all analysis tests."""

    def setUp(self):
        tracks = TEST_DATA.get("Tracks", {})
        self.df = pd.DataFrame.from_dict(tracks, orient="index")

    def assertOutputExists(self, out, ext="png"):
        if not out.endswith(f".{ext}"):
            out = f"{out}.{ext}"
        self.assertTrue(
            os.path.exists(out), f"Expected output file {out} does not exist."
        )
        self.assertGreater(os.path.getsize(out), 0, f"Output file {out} is empty.")


class TestAllAnalyses(AnalysisTestBase):
    """Test case for base analysis class."""

    pass  # pylint:disable=unnecessary-pass


class TestAllAnalysesEmptyData(AnalysisTestBase):
    """Test all analyses with an empty DataFrame."""

    def setUp(self):
        # Set up an empty DataFrame with no columns
        self.df = pd.DataFrame()


def get_analysis_modules():
    """Get a list of all analysis modules in the src/analysis directory."""
    files = glob("src/analysis/*.py")
    modules = []
    for f in files:
        name = os.path.basename(f)
        if name.startswith("_"):
            continue
        modules.append(name.replace(".py", ""))
    return modules


def add_dynamic_tests():
    """Dynamically add test methods for each analysis module."""

    def make_test(m_name, empty=False):
        def test_func(self):
            mod = importlib.import_module(f"src.analysis.{m_name}")
            params = {"top": 25}
            with tempfile.TemporaryDirectory() as tmpdir:
                out = os.path.join(tmpdir, m_name)
                if empty:
                    try:
                        mod.run(self.df, params, out)
                    except Exception as e:
                        if not isinstance(e, ValueError):
                            raise
                else:
                    mod.run(self.df, params, out)
                    ext = "csv" if m_name in CSV_MODULES else "png"
                    self.assertOutputExists(out, ext=ext)

        return test_func

    for module_name in get_analysis_modules():
        setattr(
            TestAllAnalyses,
            f"test_{module_name}_creates_file",
            make_test(module_name, empty=False),
        )
        setattr(
            TestAllAnalysesEmptyData,
            f"test_{module_name}_empty_data",
            make_test(module_name, empty=True),
        )


add_dynamic_tests()
