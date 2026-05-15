import yaml
import os
from pathlib import Path


def load_config():
    """
    Load configuration from config.yaml file.

    Returns:
        dict: Configuration dictionary with all settings
    """
    config_path = Path(__file__).parent / "config.yaml"

    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found at {config_path}")

    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)

    return config or {}


def get_default_download_path():
    """
    Get the default download path from configuration.
    Expands ~ to the user's home directory.

    Returns:
        str: Expanded path to the default download directory
    """
    config = load_config()
    default_path = config.get('default_download_path', '~/Movies/')

    # Expand ~ to home directory
    expanded_path = os.path.expanduser(default_path)

    return expanded_path


def set_download_path(path):
    """
    Set the default download path in the configuration file.

    Args:
        path (str): The new download path (can include ~)

    Returns:
        None
    """
    config_path = Path(__file__).parent / "config.yaml"

    # Load current config
    config = load_config()

    # Update the download path
    config['default_download_path'] = path

    # Write back to file
    with open(config_path, 'w') as file:
        yaml.safe_dump(config, file, default_flow_style=False)
