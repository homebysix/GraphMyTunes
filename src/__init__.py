import os
import plistlib

import yaml

# GraphMyTunes version
__version__ = "1.1.0"


def load_config(config_path: str) -> dict:
    """Load configuration from a YAML file."""
    if not os.path.exists(config_path):
        return {}
    with open(config_path, encoding="utf-8") as file:
        config = yaml.safe_load(file)
    return config


def load_itunes_xml(file_path: str) -> dict:
    """Load iTunes XML file and return its contents as a dictionary."""
    with open(file_path, "rb") as f:
        plist_data = plistlib.load(f)
    return plist_data
