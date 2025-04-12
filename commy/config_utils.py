"""
Configuration utilities for the commy tool.
Handles loading and parsing YAML configuration from ~/.commy/config.yaml.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

DEFAULT_CONFIG = {
    "ai": {
        "provider": "openai",
        "model": "gpt-3.5-turbo",
        "temperature": 0.7,
        "max_tokens": 100,
        "api_key": "",
    },
    "commit_style": "conventional",
    "diff_truncation_limit": 4000,  # Characters
}


def get_config_path() -> Path:
    """Return the path to the configuration file."""
    return Path.home() / ".commy" / "config.yaml"


def create_default_config(config_path: Path) -> None:
    """Create a default configuration file if it doesn't exist."""
    if not config_path.parent.exists():
        config_path.parent.mkdir(parents=True, exist_ok=True)

    with open(config_path, "w") as f:
        yaml.dump(DEFAULT_CONFIG, f, default_flow_style=False)


def load_config() -> Dict[str, Any]:
    """Load the configuration from the YAML file."""
    config_path = get_config_path()

    if not config_path.exists():
        create_default_config(config_path)
        print(f"Created default configuration at {config_path}")
        print("Please update it with your AI provider API key.")

    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        # Merge with defaults to ensure all required fields exist
        merged_config = DEFAULT_CONFIG.copy()
        if config:
            _merge_dicts(merged_config, config)

        return merged_config
    except Exception as e:
        print(f"Error loading configuration: {e}")
        print("Using default configuration.")
        return DEFAULT_CONFIG


def _merge_dicts(base: Dict[str, Any], overlay: Dict[str, Any]) -> None:
    """Recursively merge overlay dict into base dict."""
    for k, v in overlay.items():
        if k in base and isinstance(base[k], dict) and isinstance(v, dict):
            _merge_dicts(base[k], v)
        else:
            base[k] = v


def get_api_key() -> Optional[str]:
    """
    Get the API key from the configuration or environment variable.
    Prioritizes environment variable over config file.
    """
    env_var = "COMMY_API_KEY"
    config = load_config()

    # First check environment variable
    api_key = os.environ.get(env_var)
    if api_key:
        return api_key

    # Then check config file
    return config["ai"]["api_key"]
