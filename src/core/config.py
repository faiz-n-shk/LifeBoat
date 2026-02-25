"""
Configuration Management
Handles loading and reloading of config.yaml
"""
import yaml
from pathlib import Path
from typing import Any, Dict
from PyQt6.QtCore import QObject, pyqtSignal

from src.core.constants import APP_NAME, APP_VERSION, APP_AUTHOR
from src.core.config_template import create_default_config

# Paths
BASE_DIR = Path(__file__).parent.parent.parent
CONFIG_DIR = BASE_DIR / "config"
CONFIG_FILE = CONFIG_DIR / "config.yaml"
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"

# Ensure directories exist
CONFIG_DIR.mkdir(exist_ok=True, parents=True)
DATA_DIR.mkdir(exist_ok=True, parents=True)
ASSETS_DIR.mkdir(exist_ok=True, parents=True)


class ConfigSignals(QObject):
    """Signals for config changes"""
    config_reloaded = pyqtSignal()
    appearance_changed = pyqtSignal()
    locale_changed = pyqtSignal()


class Config:
    """Configuration manager with hot-reload support"""
    
    def __init__(self):
        self._config: Dict[str, Any] = {}
        self.signals = ConfigSignals()
        self.load()
    
    def load(self) -> None:
        """Load configuration from file"""
        if not CONFIG_FILE.exists():
            create_default_config(CONFIG_FILE)
        
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Error loading config: {e}")
            self._config = {}
    
    def reload(self, emit_signal: bool = True) -> None:
        """
        Reload configuration from file
        
        Args:
            emit_signal: Whether to emit config_reloaded signal
        """
        self.load()
        if emit_signal:
            self.signals.config_reloaded.emit()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value if value is not None else default
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save(self) -> bool:
        """Save configuration to file"""
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                yaml.dump(self._config, f, default_flow_style=False, sort_keys=False)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False


# Global config instance
config = Config()


def ensure_config_exists() -> None:
    """Ensure config.yaml exists"""
    if not CONFIG_FILE.exists():
        create_default_config(CONFIG_FILE)
        config.load()
