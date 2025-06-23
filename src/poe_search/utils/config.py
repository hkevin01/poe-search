"""Configuration utilities."""

import os
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def load_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """Load configuration from file and environment variables.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
    """
    config = {}
    
    # Default configuration
    default_config = {
        "token": None,
        "database_url": "sqlite:///poe_search.db",
        "log_level": "INFO",
        "rate_limit_delay": 1.0,
        "max_retries": 3,
        "output_dir": "exports",
        "cache_dir": ".cache",
    }
    
    config.update(default_config)
    
    # Load from config file if it exists
    if config_path and config_path.exists():
        try:
            with open(config_path, "r") as f:
                file_config = json.load(f)
            config.update(file_config)
            logger.info(f"Loaded configuration from {config_path}")
        except Exception as e:
            logger.warning(f"Failed to load config file {config_path}: {e}")
    
    # Override with environment variables
    env_mapping = {
        "POE_TOKEN": "token",
        "DATABASE_URL": "database_url",
        "LOG_LEVEL": "log_level",
        "RATE_LIMIT_DELAY": "rate_limit_delay",
        "MAX_RETRIES": "max_retries",
        "OUTPUT_DIR": "output_dir",
        "CACHE_DIR": "cache_dir",
    }
    
    for env_var, config_key in env_mapping.items():
        if env_var in os.environ:
            value = os.environ[env_var]
            
            # Convert numeric values
            if config_key in ["rate_limit_delay"]:
                try:
                    value = float(value)
                except ValueError:
                    logger.warning(f"Invalid float value for {env_var}: {value}")
                    continue
            elif config_key in ["max_retries"]:
                try:
                    value = int(value)
                except ValueError:
                    logger.warning(f"Invalid int value for {env_var}: {value}")
                    continue
            
            config[config_key] = value
    
    return config


def save_config(config: Dict[str, Any], config_path: Optional[Path] = None) -> None:
    """Save configuration to file.
    
    Args:
        config: Configuration dictionary
        config_path: Path to save configuration
    """
    if config_path is None:
        config_path = Path.home() / ".poe-search" / "config.json"
    
    # Create directory if it doesn't exist
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
        logger.info(f"Configuration saved to {config_path}")
    except Exception as e:
        logger.error(f"Failed to save configuration to {config_path}: {e}")
        raise


def get_cache_dir(config: Dict[str, Any]) -> Path:
    """Get cache directory path.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Cache directory path
    """
    cache_dir = Path(config.get("cache_dir", ".cache"))
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def get_output_dir(config: Dict[str, Any]) -> Path:
    """Get output directory path.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Output directory path
    """
    output_dir = Path(config.get("output_dir", "exports"))
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def setup_logging(config: Dict[str, Any]) -> None:
    """Set up logging configuration.
    
    Args:
        config: Configuration dictionary
    """
    log_level = config.get("log_level", "INFO").upper()
    
    # Convert string to log level
    numeric_level = getattr(logging, log_level, logging.INFO)
    
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    
    # Set specific loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("websocket").setLevel(logging.WARNING)
