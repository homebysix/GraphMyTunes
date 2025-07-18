"""Unit tests for main.py module."""

import os
import sys
import unittest
from unittest.mock import Mock, patch

import pandas as pd

# Add the src directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import main  # noqa: E402


class TestSetupLogging(unittest.TestCase):
    """Test the setup_logging function."""

    @patch("main.logging.basicConfig")
    def test_setup_logging_debug_true(self, mock_basic_config):
        """Test logging setup with debug mode."""
        main.setup_logging(debug=True)
        mock_basic_config.assert_called_once_with(
            level=main.logging.DEBUG,
            format="%(asctime)s [%(levelname)s] %(message)s {%(filename)s:%(lineno)d}",
        )

    @patch("main.logging.basicConfig")
    def test_setup_logging_debug_false(self, mock_basic_config):
        """Test logging setup without debug mode."""
        main.setup_logging(debug=False)
        mock_basic_config.assert_called_once_with(
            level=main.logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
        )


class TestParseArgs(unittest.TestCase):
    """Test the parse_args function."""

    def test_parse_args_minimal(self):
        """Test parsing minimal arguments."""
        test_args = ["main.py", "/path/to/xml"]
        with patch("sys.argv", test_args):
            args = main.parse_args()

        self.assertEqual(args.itunes_xml_path, "/path/to/xml")
        self.assertEqual(args.config, "config.yaml")
        self.assertEqual(args.top, 25)
        self.assertIsNone(args.output)
        self.assertFalse(args.debug)
        self.assertFalse(args.version)

    def test_parse_args_all_options(self):
        """Test parsing all available arguments."""
        test_args = [
            "main.py",
            "/path/to/xml",
            "--config",
            "custom.yaml",
            "--output",
            "/custom/output",
            "--top",
            "20",
            "--debug",
            "--version",
        ]
        with patch("sys.argv", test_args):
            args = main.parse_args()

        self.assertEqual(args.itunes_xml_path, "/path/to/xml")
        self.assertEqual(args.config, "custom.yaml")
        self.assertEqual(args.output, "/custom/output")
        self.assertEqual(args.top, 20)
        self.assertTrue(args.debug)
        self.assertTrue(args.version)

    def test_parse_args_no_xml_path(self):
        """Test parsing without XML path."""
        test_args = ["main.py"]
        with patch("sys.argv", test_args):
            args = main.parse_args()
            # Should not raise SystemExit, just have None for xml path
            self.assertIsNone(args.itunes_xml_path)


class TestRunAnalysis(unittest.TestCase):
    """Test the run_analysis function."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_config = {"top": 10}
        self.test_tracks_df = pd.DataFrame(
            {
                "Artist": ["Test Artist"],
                "Album": ["Test Album"],
                "Name": ["Test Track"],
                "Play Count": [5],
            }
        )
        self.test_args = (
            "test_analysis",
            self.test_tracks_df,
            self.test_config,
            "/test/output",
        )

    @patch("builtins.__import__")
    @patch("main.time.perf_counter")
    @patch("main.os.path.join")
    def test_run_analysis_success(self, mock_join, mock_perf_counter, mock_import):
        """Test successful analysis run."""
        # Mock time.perf_counter to return predictable values
        mock_perf_counter.side_effect = [0.0, 1.0]  # start and end times

        # Mock os.path.join
        mock_join.return_value = "/test/output/test_analysis"

        # Mock the imported analysis module
        mock_module = Mock()
        mock_module.run.return_value = "/test/output/test_analysis.png"
        mock_import.return_value = mock_module

        # Run the analysis
        result = main.run_analysis(self.test_args)

        # Verify the result
        self.assertEqual(
            result, ("test_analysis", "/test/output/test_analysis.png", 1.0)
        )

        # Verify the module was imported and run was called
        mock_import.assert_called_once_with(
            "src.analysis.test_analysis", fromlist=["run"]
        )
        mock_module.run.assert_called_once()

    @patch("builtins.__import__")
    @patch("main.time.perf_counter")
    @patch("main.os.path.join")
    @patch("builtins.print")
    def test_run_analysis_import_error(
        self, mock_print, mock_join, mock_perf_counter, mock_import
    ):
        """Test analysis run with import error."""
        # Mock time.perf_counter to return predictable values
        mock_perf_counter.side_effect = [0.0, 1.0]

        # Mock os.path.join
        mock_join.return_value = "/test/output/test_analysis"

        # Mock import to raise ImportError
        mock_import.side_effect = ImportError("Module not found")

        # Run the analysis
        result = main.run_analysis(self.test_args)

        # Verify the result indicates failure
        self.assertEqual(result, ("test_analysis", "", 1.0))

        # Verify error was printed
        mock_print.assert_called_once_with(
            "Analysis module 'test_analysis' not found: Module not found"
        )

    @patch("builtins.__import__")
    @patch("main.time.perf_counter")
    @patch("main.os.path.join")
    @patch("builtins.print")
    def test_run_analysis_attribute_error(
        self, mock_print, mock_join, mock_perf_counter, mock_import
    ):
        """Test analysis run with missing run function."""
        # Mock time.perf_counter to return predictable values
        mock_perf_counter.side_effect = [0.0, 1.0]

        # Mock os.path.join
        mock_join.return_value = "/test/output/test_analysis"

        # Mock module without run function
        mock_module = Mock()
        del mock_module.run
        mock_import.return_value = mock_module

        # Run the analysis
        result = main.run_analysis(self.test_args)

        # Verify the result indicates failure
        self.assertEqual(result, ("test_analysis", "", 1.0))

        # Verify error was printed
        mock_print.assert_called_once_with(
            "Module 'test_analysis' does not have a run() function."
        )

    @patch("builtins.__import__")
    @patch("main.time.perf_counter")
    @patch("main.os.path.join")
    @patch("builtins.print")
    def test_run_analysis_general_exception(
        self, mock_print, mock_join, mock_perf_counter, mock_import
    ):
        """Test analysis run with general exception."""
        # Mock time.perf_counter to return predictable values
        mock_perf_counter.side_effect = [0.0, 1.0]

        # Mock os.path.join
        mock_join.return_value = "/test/output/test_analysis"

        # Mock module with run function that raises exception
        mock_module = Mock()
        mock_module.run.side_effect = Exception("Test error")
        mock_import.return_value = mock_module

        # Run the analysis
        result = main.run_analysis(self.test_args)

        # Verify the result indicates failure
        self.assertEqual(result, ("test_analysis", "", 1.0))

        # Verify error was printed
        mock_print.assert_called_once_with(
            "Error running analysis 'test_analysis': Test error"
        )


class TestMain(unittest.TestCase):
    """Test the main function."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_config = {"top": 10}
        self.test_tracks = {
            "1": {
                "Artist": "Test Artist",
                "Album": "Test Album",
                "Name": "Test Track",
                "Play Count": 5,
            }
        }
        self.test_plist = {"Tracks": self.test_tracks}

    @patch("main.parse_args")
    @patch("main.load_config")
    @patch("main.setup_logging")
    @patch("os.path.exists")
    @patch("os.path.splitext")
    @patch("os.path.isfile")
    @patch("os.makedirs")
    @patch("main.load_itunes_xml")
    @patch("sys.exit")
    def test_main_version_flag(
        self,
        mock_exit,
        mock_load_xml,
        mock_makedirs,
        mock_isfile,
        mock_splitext,
        mock_exists,
        mock_setup_logging,
        mock_load_config,
        mock_parse_args,
    ):
        """Test main function with --version flag."""
        mock_args = Mock()
        mock_args.version = True
        mock_args.debug = False
        mock_args.itunes_xml_path = "/test/file.xml"  # Add this to prevent errors
        mock_args.top = 10  # Add required attributes
        mock_args.output = None
        mock_parse_args.return_value = mock_args
        mock_load_config.return_value = self.test_config
        mock_exists.return_value = True
        mock_splitext.return_value = ("/test/file", ".xml")
        mock_isfile.return_value = False
        mock_load_xml.return_value = self.test_plist

        with patch("builtins.print") as mock_print:
            main.main()

        mock_print.assert_called_once_with("GraphMyTunes 1.1.0")
        mock_exit.assert_called_once_with(0)

    @patch("main.parse_args")
    @patch("main.load_config")
    @patch("main.setup_logging")
    @patch("main.logging.error")
    @patch("os.path.splitext")
    @patch("os.path.isfile")
    @patch("os.makedirs")
    @patch("main.load_itunes_xml")
    @patch("sys.exit")
    def test_main_no_xml_path(
        self,
        mock_exit,
        mock_load_xml,
        mock_makedirs,
        mock_isfile,
        mock_splitext,
        mock_log_error,
        mock_setup_logging,
        mock_load_config,
        mock_parse_args,
    ):
        """Test main function without XML path."""
        mock_args = Mock()
        mock_args.version = False
        mock_args.debug = False
        mock_args.itunes_xml_path = None
        mock_args.top = 10
        mock_parse_args.return_value = mock_args
        mock_load_config.return_value = self.test_config
        mock_load_xml.return_value = self.test_plist
        mock_exit.side_effect = SystemExit(1)  # Make sys.exit actually exit

        with self.assertRaises(SystemExit):
            main.main()

        mock_log_error.assert_called_once_with("Error: iTunes XML path is required.")
        mock_exit.assert_called_once_with(1)

    @patch("main.parse_args")
    @patch("main.load_config")
    @patch("main.setup_logging")
    @patch("main.logging.error")
    @patch("os.path.splitext")
    @patch("os.path.isfile")
    @patch("os.makedirs")
    @patch("main.load_itunes_xml")
    @patch("sys.exit")
    def test_main_invalid_top_value(
        self,
        mock_exit,
        mock_load_xml,
        mock_makedirs,
        mock_isfile,
        mock_splitext,
        mock_log_error,
        mock_setup_logging,
        mock_load_config,
        mock_parse_args,
    ):
        """Test main function with invalid --top value."""
        mock_args = Mock()
        mock_args.version = False
        mock_args.debug = False
        mock_args.itunes_xml_path = "/test/file.xml"
        mock_args.top = 0  # Invalid value
        mock_args.output = None
        mock_parse_args.return_value = mock_args
        mock_load_config.return_value = self.test_config
        mock_splitext.return_value = ("/test/file", ".xml")
        mock_load_xml.return_value = self.test_plist
        mock_exit.side_effect = SystemExit(1)  # Make sys.exit actually exit

        with self.assertRaises(SystemExit):
            main.main()

        mock_log_error.assert_called_once_with(
            "'--top' must be an integer greater than zero."
        )
        mock_exit.assert_called_once_with(1)

    @patch("main.parse_args")
    @patch("main.load_config")
    @patch("main.setup_logging")
    @patch("main.logging.error")
    @patch("os.path.exists")
    @patch("os.path.splitext")
    @patch("os.path.isfile")
    @patch("os.makedirs")
    @patch("sys.exit")
    def test_main_nonexistent_xml_file(
        self,
        mock_exit,
        mock_makedirs,
        mock_isfile,
        mock_splitext,
        mock_exists,
        mock_log_error,
        mock_setup_logging,
        mock_load_config,
        mock_parse_args,
    ):
        """Test main function with nonexistent XML file."""
        mock_args = Mock()
        mock_args.version = False
        mock_args.debug = False
        mock_args.itunes_xml_path = "/nonexistent/file.xml"
        mock_args.top = 10
        mock_args.output = None
        mock_parse_args.return_value = mock_args
        mock_load_config.return_value = self.test_config
        mock_exists.return_value = False
        mock_splitext.return_value = ("/nonexistent/file", ".xml")
        mock_isfile.return_value = False
        mock_exit.side_effect = SystemExit(1)  # Make sys.exit actually exit

        with self.assertRaises(SystemExit):
            main.main()

        mock_log_error.assert_called_once_with(
            "The specified XML file does not exist. Please provide a valid path."
        )
        mock_exit.assert_called_once_with(1)

    @patch("main.parse_args")
    @patch("main.load_config")
    @patch("main.setup_logging")
    @patch("main.logging.error")
    @patch("os.path.exists")
    @patch("os.path.isfile")
    @patch("os.makedirs")
    @patch("main.load_itunes_xml")
    @patch("sys.exit")
    def test_main_xml_load_error(
        self,
        mock_exit,
        mock_load_xml,
        mock_makedirs,
        mock_isfile,
        mock_exists,
        mock_log_error,
        mock_setup_logging,
        mock_load_config,
        mock_parse_args,
    ):
        """Test main function with XML loading error."""
        mock_args = Mock()
        mock_args.version = False
        mock_args.debug = False
        mock_args.itunes_xml_path = "/test/file.xml"
        mock_args.top = 10
        mock_args.output = None
        mock_parse_args.return_value = mock_args
        mock_load_config.return_value = self.test_config
        mock_exists.return_value = True
        mock_isfile.return_value = False

        # Create a specific exception instance
        test_exception = Exception("XML parse error")
        mock_load_xml.side_effect = test_exception
        mock_exit.side_effect = SystemExit(1)  # Make sys.exit actually exit

        with self.assertRaises(SystemExit):
            main.main()

        mock_log_error.assert_called_once_with(
            "Failed to load XML file: %s", test_exception
        )
        mock_exit.assert_called_once_with(1)

    @patch("main.parse_args")
    @patch("main.load_config")
    @patch("main.setup_logging")
    @patch("main.logging.info")
    @patch("main.time.perf_counter")
    @patch("os.path.exists")
    @patch("os.path.splitext")
    @patch("os.path.isfile")
    @patch("os.makedirs")
    @patch("os.path.dirname")
    @patch("os.path.join")
    @patch("main.glob.glob")
    @patch("main.load_itunes_xml")
    @patch("main.concurrent.futures.ProcessPoolExecutor")
    def test_main_success(
        self,
        mock_executor,
        mock_load_xml,
        mock_glob,
        mock_join,
        mock_dirname,
        mock_makedirs,
        mock_isfile,
        mock_splitext,
        mock_exists,
        mock_perf_counter,
        mock_log_info,
        mock_setup_logging,
        mock_load_config,
        mock_parse_args,
    ):
        """Test successful main function execution."""
        mock_args = Mock()
        mock_args.version = False
        mock_args.debug = False
        mock_args.itunes_xml_path = "/test/file.xml"
        mock_args.top = 10
        mock_args.output = None
        mock_parse_args.return_value = mock_args
        mock_load_config.return_value = self.test_config
        mock_exists.return_value = True
        mock_splitext.return_value = ("/test/file", ".xml")
        mock_isfile.return_value = False
        mock_load_xml.return_value = self.test_plist

        # Mock time.perf_counter for timing
        mock_perf_counter.side_effect = [0.0, 2.0]  # start and end times

        # Mock file system operations
        mock_dirname.return_value = "/test/src"
        mock_join.side_effect = lambda *args: "/".join(args)
        mock_glob.return_value = ["/test/src/analysis/test_analysis.py"]

        # Mock the ProcessPoolExecutor
        mock_pool = Mock()
        mock_executor.return_value.__enter__.return_value = mock_pool
        mock_pool.map.return_value = [
            ("test_analysis", "/test/output/test_analysis.png", 1.0)
        ]

        main.main()

        # Verify setup_logging was called with correct debug flag
        mock_setup_logging.assert_called_once_with(False)

        # Verify output directory was created
        mock_makedirs.assert_called_once_with("/test/file", exist_ok=True)

        # Verify XML loading was called
        mock_load_xml.assert_called_once_with("/test/file.xml")

        # Verify final logging message
        mock_log_info.assert_any_call("%d analyses completed in %.2f seconds.", 1, 2.0)

    @patch("main.parse_args")
    @patch("main.load_config")
    @patch("main.setup_logging")
    @patch("main.logging.error")
    @patch("main.logging.info")
    @patch("main.time.perf_counter")
    @patch("os.path.exists")
    @patch("os.path.splitext")
    @patch("os.path.isfile")
    @patch("os.makedirs")
    @patch("os.path.dirname")
    @patch("os.path.join")
    @patch("main.glob.glob")
    @patch("main.load_itunes_xml")
    @patch("sys.exit")
    def test_main_empty_dataframe(
        self,
        mock_exit,
        mock_load_xml,
        mock_glob,
        mock_join,
        mock_dirname,
        mock_makedirs,
        mock_isfile,
        mock_splitext,
        mock_exists,
        mock_perf_counter,
        mock_log_info,
        mock_log_error,
        mock_setup_logging,
        mock_load_config,
        mock_parse_args,
    ):
        """Test main function with empty DataFrame."""
        mock_args = Mock()
        mock_args.version = False
        mock_args.debug = True
        mock_args.itunes_xml_path = "/test/file.xml"
        mock_args.top = 10
        mock_args.output = "/custom/output"
        mock_parse_args.return_value = mock_args
        mock_load_config.return_value = self.test_config
        mock_exists.return_value = True
        mock_splitext.return_value = ("/test/file", ".xml")
        mock_isfile.return_value = False
        mock_load_xml.return_value = {"Tracks": {}}  # Empty tracks dict

        main.main()

        # Verify setup_logging was called with debug=True
        mock_setup_logging.assert_called_once_with(True)

        # Verify custom output directory was created
        mock_makedirs.assert_called_once_with("/custom/output", exist_ok=True)

        # Verify XML loading was called
        mock_load_xml.assert_called_once_with("/test/file.xml")

        # Verify error was logged and exit was called
        mock_log_error.assert_called_once_with("No tracks found in the XML file.")
        mock_exit.assert_called_once_with(1)


if __name__ == "__main__":
    unittest.main()
