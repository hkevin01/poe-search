"""Configuration management for Poe Search."""

import json
import logging
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

import keyring  # type: ignore
from dotenv import load_dotenv

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
class RateLimitSettings:
    """Rate limiting settings."""
    enable_rate_limiting: bool = True
    max_calls_per_minute: int = 8
    retry_attempts: int = 3
    base_delay_seconds: int = 5
    max_delay_seconds: int = 60
    jitter_range: float = 0.5
    show_rate_limit_warnings: bool = True
    prompt_for_token_costs: bool = True


@dataclass
class PoeSearchConfig:
    """Main configuration class."""
    # API settings - support both old and new formats
    poe_token: str = ""  # Legacy single token
    poe_tokens: Dict[str, str] = field(default_factory=lambda: {
        "p-b": "",
        "p-lat": "",
        "formkey": ""
    })  # New cookie-based tokens
    
    # Official API settings
    poe_api_key: str = ""  # Official API key from poe.com/api_key
    api_type: str = "wrapper"  # "wrapper" or "official"
    
    database_url: str = "sqlite:///poe_search.db"
    
    # GUI settings
    gui: GUISettings = field(default_factory=GUISettings)
    
    # Feature settings
    search: SearchSettings = field(default_factory=SearchSettings)
    sync: SyncSettings = field(default_factory=SyncSettings)
    export: ExportSettings = field(default_factory=ExportSettings)
    rate_limit: RateLimitSettings = field(default_factory=RateLimitSettings)
    
    # Advanced settings
    log_level: str = "INFO"
    enable_debug_mode: bool = False
    cache_size_mb: int = 100
    
    def get_poe_tokens(self) -> Dict[str, str]:
        """Get Poe tokens, supporting both old and new formats.
        
        Returns:
            Dictionary of Poe tokens (p-b, p-lat, formkey)
        """
        # If we have the new format, use it
        if self.poe_tokens and self.poe_tokens.get("p-b"):
            return self.poe_tokens
        
        # Fall back to old format
        if self.poe_token:
            return {
                "p-b": self.poe_token,
                "p-lat": self.poe_token,  # Use same token for both
                "formkey": ""
            }
        
        return {"p-b": "", "p-lat": "", "formkey": ""}
    
    def has_valid_tokens(self) -> bool:
        """Check if we have valid Poe tokens.
        
        Returns:
            True if we have at least p-b token
        """
        tokens = self.get_poe_tokens()
        return bool(tokens.get("p-b"))
    
    def get_poe_api_key(self) -> str:
        """Get Poe API key from config or secure sources."""
        if self.poe_api_key:
            return self.poe_api_key
        return get_poe_api_key()
    
    def get_api_type(self) -> str:
        """Get the current API type.
        
        Returns:
            "wrapper" or "official"
        """
        return self.api_type
    
    def set_api_type(self, api_type: str) -> None:
        """Set the API type.
        
        Args:
            api_type: "wrapper" or "official"
        """
        if api_type not in ["wrapper", "official"]:
            raise ValueError("API type must be 'wrapper' or 'official'")
        self.api_type = api_type
    
    def copy(self) -> 'PoeSearchConfig':
        """Create a copy of the configuration.
        
        Returns:
            Copy of the configuration
        """
        return PoeSearchConfig(
            poe_token=self.poe_token,
            poe_tokens=self.poe_tokens.copy(),
            poe_api_key=self.poe_api_key,
            api_type=self.api_type,
            database_url=self.database_url,
            gui=self.gui,
            search=self.search,
            sync=self.sync,
            export=self.export,
            rate_limit=self.rate_limit,
            log_level=self.log_level,
            enable_debug_mode=self.enable_debug_mode,
            cache_size_mb=self.cache_size_mb
        )


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
                    secrets = json.load(f)
                    logger.info("Loaded secrets from config/secrets.json")
                    return secrets
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
        if api_key := secrets.get("api_key"):
            config.poe_token = api_key
            logger.info("Loaded API key from secrets file")
        elif poe_api_key := secrets.get("poe_api_key"):
            config.poe_token = poe_api_key
            logger.info("Loaded Poe API key from secrets file")
        
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
            poe_tokens=data.get("poe_tokens", {
                "p-b": "",
                "p-lat": "",
                "formkey": ""
            }),
            database_url=data.get("database_url", "sqlite:///poe_search.db"),
            gui=GUISettings(**gui_data),
            search=SearchSettings(**search_data),
            sync=SyncSettings(**sync_data),
            export=ExportSettings(**export_data),
            rate_limit=RateLimitSettings(**data.get("rate_limit", {})),
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
        data["rate_limit"] = asdict(config.rate_limit)
        
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
        for section in ["gui", "search", "sync", "export", "rate_limit"]:
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


def load_poe_tokens_from_file(
    force_refresh: bool = False, max_age_hours: int = 36
) -> Dict[str, str]:
    """Load Poe.com authentication tokens from file using token manager.
    
    Args:
        force_refresh: Force token refresh even if current tokens are fresh
        max_age_hours: Maximum age in hours before tokens are considered stale
        
    Returns:
        Dictionary of tokens (p-b, p-lat, formkey) or empty dict if failed
    """
    try:
        from poe_search.utils.token_manager import TokenManager
        
        manager = TokenManager()
        
        if force_refresh:
            # Force interactive refresh
            logger.info("Forcing token refresh")
            success = manager.interactive_refresh()
            if not success:
                logger.error("Token refresh failed")
                return {}
            
        # Load tokens (will check freshness)
        tokens = manager.load_tokens()
        if tokens:
            # Check if fresh enough
            if manager.are_tokens_fresh(max_age_hours):
                return tokens
            else:
                logger.warning(f"Tokens are older than {max_age_hours} hours")
                return {}
        else:
            logger.warning("No tokens found")
            return {}
            
    except Exception as e:
        logger.error(f"Error loading tokens: {e}")
        return {}


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


def get_poe_api_key() -> str:
    """
    Securely load the Poe API key in this order:
    1. Environment variable (including .env via python-dotenv)
    2. OS keyring (system secret store)
    3. config/secrets.json (legacy fallback)
    """
    # 1. Load from .env or environment variable
    load_dotenv()
    api_key = os.getenv("POE_API_KEY")
    if api_key:
        return api_key

    # 2. Try OS keyring
    try:
        api_key = keyring.get_password("poe_search", "poe_api_key")
        if api_key:
            return api_key
    except Exception:
        pass

    # 3. Fallback: secrets.json
    secrets_path = Path("config/secrets.json")
    if secrets_path.exists():
        try:
            with open(secrets_path, "r", encoding="utf-8") as f:
                secrets = json.load(f)
            api_key = secrets.get("poe_api_key", "")
            if api_key:
                return api_key
        except Exception:
            pass
    return ""


# User guidance:
# To set your Poe API key securely, you can:
# 1. Set the POE_API_KEY environment variable (export POE_API_KEY=...)
# 2. Add POE_API_KEY=... to a .env file in your project root
# 3. Store it in your OS keyring using:
#    import keyring; keyring.set_password(
#        'poe_search', 'poe_api_key', 'YOUR_KEY')
# 4. (Legacy) Add it to config/secrets.json as
#    {"poe_api_key": "YOUR_KEY"}
