"""Configuration management for Poe Search."""

import json
import logging
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class GUISettings:
    """GUI-specific settings."""
    window_width: int = 1400
    window_height: int = 900
    window_x: int = 100
    window_y: int = 100
    theme: str = "dark"
    font_size: int = 12
    auto_refresh_interval: int = 30
    show_toolbar: bool = True
    show_status_bar: bool = True
    remember_window_position: bool = True
    remember_window_size: bool = True


@dataclass
class SearchSettings:
    """Search-specific settings."""
    default_search_limit: int = 50
    enable_fuzzy_search: bool = True
    enable_regex_search: bool = True
    case_sensitive: bool = False
    search_in_messages: bool = True
    search_in_titles: bool = True
    highlight_search_results: bool = True
    auto_search_delay: int = 500  # milliseconds


@dataclass
class SyncSettings:
    """Sync-specific settings."""
    auto_sync_on_startup: bool = False
    sync_interval: int = 3600  # seconds
    sync_days_back: int = 7
    sync_batch_size: int = 100
    retry_failed_syncs: bool = True
    max_retry_attempts: int = 3


@dataclass
class ExportSettings:
    """Export-specific settings."""
    default_export_format: str = "json"
    default_export_directory: str = ""
    include_metadata: bool = True
    include_messages: bool = True
    compress_exports: bool = False
    export_filename_template: str = "poe_conversations_{date}_{time}"


@dataclass
class PoeSearchConfig:
    """Main configuration class."""
    # API settings
    poe_token: str = ""
    database_url: str = "sqlite:///poe_search.db"
    
    # GUI settings
    gui: GUISettings = field(default_factory=GUISettings)
    
    # Feature settings
    search: SearchSettings = field(default_factory=SearchSettings)
    sync: SyncSettings = field(default_factory=SyncSettings)
    export: ExportSettings = field(default_factory=ExportSettings)
    
    # Advanced settings
    log_level: str = "INFO"
    enable_debug_mode: bool = False
    cache_size_mb: int = 100


class ConfigManager:
    """Configuration manager for Poe Search."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize configuration manager.
        
        Args:
            config_path: Path to configuration file
        """
        if config_path is None:
            # Use default config path
            config_dir = self._get_default_config_dir()
            config_path = config_dir / "config.json"
        
        self.config_path = Path(config_path)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load or create default configuration
        self.config = self._load_config()
    
    def _get_default_config_dir(self) -> Path:
        """Get default configuration directory."""
        # Try environment variable first
        if config_dir := os.getenv("POE_SEARCH_CONFIG_DIR"):
            return Path(config_dir)
        
        # Use XDG config directory on Linux
        if xdg_config := os.getenv("XDG_CONFIG_HOME"):
            return Path(xdg_config) / "poe-search"
        
        # Use home directory
        return Path.home() / ".poe-search"
    
    def _load_secrets(self) -> Dict[str, str]:
        """Load secrets from config/secrets.json file."""
        secrets_path = Path("config/secrets.json")
        if secrets_path.exists():
            try:
                with open(secrets_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(
                    f"Failed to load secrets from {secrets_path}: {e}"
                )
        return {}
    
    def _load_config(self) -> PoeSearchConfig:
        """Load configuration from file or create default."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                config = self._dict_to_config(data)
            except Exception as e:
                logger.warning(
                    f"Failed to load config from {self.config_path}: {e}"
                )
                logger.info("Creating default configuration")
                config = PoeSearchConfig()
        else:
            # Create default configuration
            config = PoeSearchConfig()
        
        # Load API key from secrets file
        secrets = self._load_secrets()
        if api_key := secrets.get("poe_api_key"):
            config.poe_token = api_key
            logger.info("Loaded API key from secrets file")
        
        self.save_config(config)
        return config
    
    def _dict_to_config(self, data: Dict[str, Any]) -> PoeSearchConfig:
        """Convert dictionary to configuration object."""
        # Handle nested dataclasses
        gui_data = data.get("gui", {})
        search_data = data.get("search", {})
        sync_data = data.get("sync", {})
        export_data = data.get("export", {})
        
        return PoeSearchConfig(
            poe_token=data.get("poe_token", ""),
            database_url=data.get("database_url", "sqlite:///poe_search.db"),
            gui=GUISettings(**gui_data),
            search=SearchSettings(**search_data),
            sync=SyncSettings(**sync_data),
            export=ExportSettings(**export_data),
            log_level=data.get("log_level", "INFO"),
            enable_debug_mode=data.get("enable_debug_mode", False),
            cache_size_mb=data.get("cache_size_mb", 100),
        )
    
    def _config_to_dict(self, config: PoeSearchConfig) -> Dict[str, Any]:
        """Convert configuration object to dictionary."""
        data = asdict(config)
        
        # Handle nested dataclasses
        data["gui"] = asdict(config.gui)
        data["search"] = asdict(config.search)
        data["sync"] = asdict(config.sync)
        data["export"] = asdict(config.export)
        
        return data
    
    def save_config(
        self, 
        config: Optional[PoeSearchConfig] = None
    ) -> None:
        """Save configuration to file.
        
        Args:
            config: Configuration to save (uses current if None)
        """
        if config is None:
            config = self.config
        
        try:
            data = self._config_to_dict(config)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Configuration saved to {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            raise
    
    def get_config(self) -> PoeSearchConfig:
        """Get current configuration."""
        return self.config
    
    def update_config(self, updates: Dict[str, Any]) -> None:
        """Update configuration with new values.
        
        Args:
            updates: Dictionary of configuration updates
        """
        # Update main config
        for key, value in updates.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        
        # Update nested configs
        for section in ["gui", "search", "sync", "export"]:
            if section in updates:
                section_data = updates[section]
                section_config = getattr(self.config, section)
                for key, value in section_data.items():
                    if hasattr(section_config, key):
                        setattr(section_config, key, value)
        
        self.save_config()
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to default values."""
        self.config = PoeSearchConfig()
        self.save_config()
        logger.info("Configuration reset to defaults")
    
    def get_token(self) -> str:
        """Get Poe API token."""
        # Try to load from secrets file first
        secrets = self._load_secrets()
        if api_key := secrets.get("poe_api_key"):
            return api_key
        return self.config.poe_token
    
    def set_token(self, token: str) -> None:
        """Set Poe token in configuration.
        
        Args:
            token: Poe authentication token
        """
        self.config.poe_token = token
        self.save_config()
        logger.info("Poe token updated")
    
    def get_database_url(self) -> str:
        """Get database URL from configuration."""
        return self.config.database_url
    
    def set_database_url(self, url: str) -> None:
        """Set database URL in configuration.
        
        Args:
            url: Database connection URL
        """
        self.config.database_url = url
        self.save_config()
        logger.info(f"Database URL updated to {url}")


# Global configuration manager instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Get global configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def load_config(config_path: Optional[Path] = None) -> PoeSearchConfig:
    """Load configuration from file.
    
    Args:
        config_path: Optional path to configuration file
        
    Returns:
        Configuration object
    """
    manager = ConfigManager(config_path)
    return manager.get_config()


def save_config(
    config: PoeSearchConfig, 
    config_path: Optional[Path] = None
) -> None:
    """Save configuration to file.
    
    Args:
        config: Configuration to save
        config_path: Optional path to configuration file
    """
    manager = ConfigManager(config_path)
    manager.save_config(config)


def get_config() -> PoeSearchConfig:
    """Get current configuration."""
    return get_config_manager().get_config()


def update_config(updates: Dict[str, Any]) -> None:
    """Update configuration with new values.
    
    Args:
        updates: Dictionary of configuration updates
    """
    get_config_manager().update_config(updates)
