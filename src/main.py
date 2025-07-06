import argparse
import concurrent.futures
import glob
import logging
import os
import sys
import time
from typing import Any, Dict, Tuple

import pandas as pd

from src import __version__, load_config, load_itunes_xml


def setup_logging(debug: bool = False) -> None:
    """Set up logging configuration."""
    if debug:
        level = logging.DEBUG
        fmt = "%(asctime)s [%(levelname)s] %(message)s {%(filename)s:%(lineno)d}"
    else:
        level = logging.INFO
        fmt = "%(asctime)s [%(levelname)s] %(message)s"
    logging.basicConfig(level=level, format=fmt)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="GraphMyTunes: Apple Music library analysis tool."
    )
    parser.add_argument(
        "itunes_xml_path",
        type=str,
        nargs="?",
        default=None,
        help="Path to the XML file exported from Music.app.",
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Directory to store output files. Defaults to the same path as the provided XML file.",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=25,
        help="Limit output to the top N results for each analysis. (Default: 25)",
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show the version of the project and exit.",
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Path to the config.yaml file.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging.",
    )
    return parser.parse_args()


def run_analysis(
    args: Tuple[str, pd.DataFrame, Dict[str, Any], str],
) -> Tuple[str, str, float]:
    """Run a specific analysis in a separate process."""
    analysis, tracks_df, config, output_dir = args

    def analyze(
        tracks: pd.DataFrame,
        analysis_name: str,
        analysis_params: dict,
        output_path: str,
    ) -> str:
        output_file = ""
        try:
            module = __import__(f"src.analysis.{analysis_name}", fromlist=["run"])
            output_file = module.run(tracks, analysis_params, output_path)
        except ImportError as e:
            print(f"Analysis module '{analysis_name}' not found: {e}")
        except AttributeError:
            print(f"Module '{analysis_name}' does not have a run() function.")
        except Exception as e:
            print(f"Error running analysis '{analysis_name}': {e}")
        return output_file

    start_time = time.perf_counter()
    params: Dict[str, Any] = {}

    # Add analysis-specific parameters if present
    params = config.get("analyses", {}).get(analysis, {}) if config else {}

    # Add general parameters, overwriting analysis-specific ones that conflict
    if config:
        for k, v in config.items():
            if k != "analyses":
                params[k] = v

    output_path = os.path.join(output_dir, f"{analysis}")
    output_file = analyze(tracks_df, analysis, params, output_path)
    elapsed = time.perf_counter() - start_time

    return analysis, output_file, elapsed


def main() -> None:
    """Main entry point for GraphMyTunes."""

    # Parse command line arguments and configuration yaml
    args = parse_args()
    config = load_config(args.config)
    main_start_time = time.perf_counter()

    # Set up logging
    setup_logging(args.debug)

    # If --version is specified, print version and exit
    if args.version:
        print(f"GraphMyTunes {__version__}")
        sys.exit(0)

    # Check if iTunes XML path is provided
    if not args.itunes_xml_path:
        logging.error("Error: iTunes XML path is required.")
        sys.exit(1)

    # Add top N results parameter to config
    if args.top <= 0:
        logging.error("'--top' must be an integer greater than zero.")
        sys.exit(1)
    config["top"] = args.top

    # Verify iTunes XML file exists
    xml_file_path = args.itunes_xml_path
    if not xml_file_path or not os.path.exists(xml_file_path):
        logging.error(
            "The specified XML file does not exist. Please provide a valid path."
        )
        sys.exit(1)

    # Determine (and create) output directory
    if args.output:
        output_dir = args.output
    else:
        output_dir, _ = os.path.splitext(xml_file_path)
    if os.path.isfile(output_dir):
        logging.error(
            "The output path '%s' is a file. Please use --output to specify a directory.",
            output_dir,
        )
        sys.exit(1)
    os.makedirs(output_dir, exist_ok=True)

    logging.info("Loading iTunes XML file from %s", xml_file_path)
    try:
        plist_data = load_itunes_xml(xml_file_path)
    except Exception as e:
        logging.error("Failed to load XML file: %s", e)
        sys.exit(1)

    # Count tracks, artists, and albums
    tracks = plist_data.get("Tracks", {})
    track_count = len(tracks)
    artist_count = len({x.get("Artist") for x in tracks.values() if x.get("Artist")})
    album_count = len({x.get("Album") for x in tracks.values() if x.get("Album")})

    logging.info(
        "Successfully loaded iTunes XML file containing "
        "%d track%s, %d artist%s, and %d album%s.",
        track_count,
        "s" if track_count != 1 else "",
        artist_count,
        "s" if artist_count != 1 else "",
        album_count,
        "s" if album_count != 1 else "",
    )

    # Convert tracks to DataFrame for easier analysis
    tracks_df = pd.DataFrame.from_dict(tracks, orient="index")
    if tracks_df.empty:
        logging.error("No tracks found in the XML file.")
        sys.exit(1)

    # List of analyses to run and their input parameters if specified in config
    analysis_dir = os.path.join(os.path.dirname(__file__), "analysis")
    analyses = [
        os.path.splitext(os.path.basename(f))[0]
        for f in glob.glob(os.path.join(analysis_dir, "*.py"))
        if not os.path.basename(f).endswith("_.py")
    ]
    analyses.sort()

    # Analyze in parallel using multiprocessing
    analysis_args = [(analysis, tracks_df, config, output_dir) for analysis in analyses]
    results = []
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for analysis, output_file, elapsed in executor.map(run_analysis, analysis_args):
            if output_file:
                logging.info(
                    "Saved output to '%s' in %.2f seconds.", output_file, elapsed
                )
            else:
                logging.error(
                    "Analysis '%s' failed in %.2f seconds. Skipping.", analysis, elapsed
                )
            results.append((analysis, output_file, elapsed))

    # Report the total run time
    main_elapsed = time.perf_counter() - main_start_time
    logging.info("%d analyses completed in %.2f seconds.", len(analyses), main_elapsed)


if __name__ == "__main__":
    main()
