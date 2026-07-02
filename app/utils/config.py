import os
import json
from typing import Dict, Any, List
from app.utils.logger import logger

DEFAULT_CONFIG: Dict[str, Any] = {
    "theme": "dark",
    "working_hours": 8.0,
    "priorities": ["Low", "Medium", "High", "Critical"],
    "statuses": ["Not Started", "In Progress", "Paused", "Completed", "Cancelled"],
    "notifications": {
        "task_duration_warning": True,
        "task_warning_hours": 2,
        "break_reminder": True,
        "break_interval_minutes": 90,
        "eod_reminder": True,
        "incomplete_task_reminder": True,
        "eod_time": "17:30"
    },
    "db_path": "tracker.db"
}

class ConfigManager:
    def __init__(self, config_path: str = "config.json"):
        self.config_path = os.path.abspath(config_path)
        self.config = {}
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """Loads configuration from JSON file or returns default config if not found."""
        if not os.path.exists(self.config_path):
            logger.info("Config file not found, creating default config.")
            self.save_config(DEFAULT_CONFIG)
            return DEFAULT_CONFIG.copy()
        
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Fill missing keys from default config
                config = DEFAULT_CONFIG.copy()
                config.update(data)
                return config
        except Exception as e:
            logger.error(f"Error reading config file: {e}. Using defaults.")
            return DEFAULT_CONFIG.copy()

    def save_config(self, config_data: Dict[str, Any] = None) -> bool:
        """Saves current configuration to JSON file."""
        if config_data:
            self.config.update(config_data)
        
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            logger.info("Configuration saved successfully.")
            return True
        except Exception as e:
            logger.error(f"Error saving config file: {e}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieves a configuration setting."""
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> bool:
        """Sets a configuration setting and saves it."""
        self.config[key] = value
        return self.save_config()

# Global config manager instance
config_manager = ConfigManager()
