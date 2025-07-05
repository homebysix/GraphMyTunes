import os
import tempfile
import unittest

import matplotlib.pyplot as plt
import pandas as pd
import pytz

from src import __version__, load_config, load_itunes_xml
from src.analysis import _utils_ as utils


class TestUtils(unittest.TestCase):
    def test_ensure_columns_pass(self):
        df = pd.DataFrame({"A": [1], "B": [2]})
        # Should not raise
        utils.ensure_columns(df, ["A", "B"])

    def test_ensure_columns_fail(self):
        df = pd.DataFrame({"A": [1]})
        with self.assertRaises(ValueError) as cm:
            utils.ensure_columns(df, ["A", "B"])
        self.assertIn("Missing columns", str(cm.exception))

    def test_rating_to_stars(self):
        s = pd.Series([100, 80, 60, 40, 20, 0, None])
        stars = utils.rating_to_stars(s)
        expected = pd.Series([5, 4, 3, 2, 1, 0, 0])
        pd.testing.assert_series_equal(stars, expected)

    def test_trim_label(self):
        self.assertEqual(utils.trim_label("A", 32), "A")
        self.assertEqual(utils.trim_label("B" * 32, 32), "B" * 32)
        self.assertEqual(utils.trim_label("C" * 40, 32), "C" * 32 + "…")

    def test_save_plot(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out = os.path.join(tmpdir, "plot_test")
            plt.plot([1, 2, 3], [4, 5, 6])
            title = "Test Plot"
            utils.save_plot(title, out, ext="png", dpi=72)
            self.assertTrue(os.path.exists(out + ".png"))
            self.assertTrue(os.path.getsize(out + ".png") > 0)

    def test_get_today_matching_tz_naive(self):
        s = pd.Series(pd.date_range("2023-01-01", periods=3))
        today = utils.get_today_matching_tz(s)
        self.assertIsInstance(today, pd.Timestamp)
        self.assertFalse(today.tzinfo)

    def test_get_today_matching_tz_aware(self):
        tz = pytz.timezone("America/Los_Angeles")
        s = pd.Series(pd.date_range("2023-01-01", periods=3, tz=tz))
        today = utils.get_today_matching_tz(s)
        self.assertIsInstance(today, pd.Timestamp)
        self.assertIsNotNone(today.tzinfo)
        self.assertEqual(str(today.tzinfo), str(tz))

    def test_zero_seconds(self):
        self.assertEqual(utils.sec_to_human_readable(0), "0s")

    def test_negative_seconds(self):
        self.assertEqual(utils.sec_to_human_readable(-10), "0s")

    def test_seconds_only(self):
        self.assertEqual(utils.sec_to_human_readable(45), "45s")

    def test_min_and_sec(self):
        self.assertEqual(utils.sec_to_human_readable(125), "2m 5s")

    def test_hrs_min_sec(self):
        self.assertEqual(utils.sec_to_human_readable(3661), "1h 1m 1s")

    def test_days_hrs_min_sec(self):
        self.assertEqual(utils.sec_to_human_readable(90061), "1d 1h 1m 1s")

    def test_yrs_days_hrs_min_sec(self):
        total_seconds = 31536000 + 86400 + 3600 + 60 + 1
        self.assertEqual(utils.sec_to_human_readable(total_seconds), "1y 1d 1h 1m 1s")

    def test_version(self):
        # Normal case
        version = __version__
        self.assertIsInstance(version, str)
        # Ensure version is strictly semver: MAJOR.MINOR.PATCH (optionally with pre-release/build)
        self.assertRegex(
            version, r"^\d+\.\d+\.\d+(-[0-9A-Za-z-.]+)?(\+[0-9A-Za-z-.]+)?$"
        )

    def test_load_config(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".yaml") as tmpfile:
            tmpfile.write(b"key: value\n")
            config_path = tmpfile.name
        config = load_config(config_path)
        self.assertEqual(config, {"key": "value"})
        os.remove(config_path)

    def test_load_itunes_xml(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xml") as tmpfile:
            tmpfile.write(
                b'<?xml version="1.0" encoding="UTF-8"?>\n'
                b'<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" '
                b'"http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n'
                b'<plist version="1.0">\n'
                b"<dict>\n"
                b"	<key>key</key>\n"
                b"	<string>value</string>\n"
                b"</dict>\n"
                b"</plist>\n"
            )
            xml_path = tmpfile.name
        plist_data = load_itunes_xml(xml_path)
        self.assertEqual(plist_data, {"key": "value"})
        os.remove(xml_path)
