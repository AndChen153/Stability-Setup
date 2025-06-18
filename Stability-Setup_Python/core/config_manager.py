"""
Configuration Management Module

Centralizes all configuration handling with validation and type safety.
Replaces scattered JSON loading throughout the application.
"""
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, field
from helper.global_helpers import get_logger


@dataclass
class EmailConfig:
    """Email configuration settings."""
    user: str = ""
    password: str = ""
    
    def is_valid(self) -> bool:
        """Check if email configuration is valid."""
        return bool(self.user and self.password)


@dataclass
class ArduinoConfig:
    """Arduino configuration settings."""
    ids: Dict[str, int] = field(default_factory=dict)
    baud_rate: int = 115200
    timeout: float = 1.0
    
    def get_arduino_id(self, hw_id: str) -> Optional[int]:
        """Get Arduino ID for given hardware ID."""
        return self.ids.get(hw_id)
    
    def set_arduino_id(self, hw_id: str, arduino_id: int) -> None:
        """Set Arduino ID for given hardware ID."""
        self.ids[hw_id] = arduino_id


@dataclass
class DataConfig:
    """Data storage and processing configuration."""
    base_dir: str = ""
    auto_save_interval: int = 20  # lines per save
    max_file_size_mb: int = 100
    
    def get_data_dir(self, trial_name: str = "") -> Path:
        """Get data directory for current trial."""
        from datetime import datetime
        date_str = datetime.now().strftime("%b-%d-%Y %H_%M_%S")
        trial_suffix = f"__{trial_name}" if trial_name else ""
        return Path(self.base_dir) / f"{date_str}{trial_suffix}"


@dataclass
class UIConfig:
    """User interface configuration."""
    theme: str = "light"
    window_geometry: Dict[str, int] = field(default_factory=lambda: {
        "width": 1200, "height": 800, "x": 100, "y": 100
    })
    auto_refresh_interval: int = 1000  # milliseconds


class ConfigManager:
    """
    Centralized configuration manager with validation and type safety.
    
    Handles loading, saving, and validation of all application settings.
    Provides a single source of truth for configuration data.
    """
    
    def __init__(self, config_file: Union[str, Path]):
        self.config_file = Path(config_file)
        self.email = EmailConfig()
        self.arduino = ArduinoConfig()
        self.data = DataConfig()
        self.ui = UIConfig()
        
        # Set default data directory relative to config file
        self.data.base_dir = str(self.config_file.parent.parent / "data")
        
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from JSON file."""
        if not self.config_file.exists():
            get_logger().log(f"Config file not found: {self.config_file}. Using defaults.")
            self._create_default_config()
            return
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self._parse_config(data)
            get_logger().log(f"Configuration loaded from {self.config_file}")
            
        except (json.JSONDecodeError, FileNotFoundError) as e:
            get_logger().log(f"Error loading config: {e}. Using defaults.")
            self._create_default_config()
    
    def _parse_config(self, data: Dict[str, Any]) -> None:
        """Parse configuration data into typed objects."""
        # Email settings
        email_data = data.get("email_settings", {})
        self.email.user = email_data.get("user", "")
        self.email.password = email_data.get("pass", "")
        
        # Arduino settings
        arduino_data = data.get("arduino_ids", {})
        self.arduino.ids = {str(k): int(v) for k, v in arduino_data.items()}
        
        # UI settings
        ui_data = data.get("ui_settings", {})
        self.ui.theme = ui_data.get("theme", "light")
        self.ui.window_geometry.update(ui_data.get("window_geometry", {}))
        
        # Data settings
        data_settings = data.get("data_settings", {})
        if "base_dir" in data_settings:
            self.data.base_dir = data_settings["base_dir"]
        self.data.auto_save_interval = data_settings.get("auto_save_interval", 20)
    
    def _create_default_config(self) -> None:
        """Create default configuration file."""
        self.save_config()
        get_logger().log(f"Created default configuration at {self.config_file}")
    
    def save_config(self) -> None:
        """Save current configuration to JSON file."""
        config_data = {
            "email_settings": {
                "user": self.email.user,
                "pass": self.email.password
            },
            "arduino_ids": self.arduino.ids,
            "ui_settings": {
                "theme": self.ui.theme,
                "window_geometry": self.ui.window_geometry
            },
            "data_settings": {
                "base_dir": self.data.base_dir,
                "auto_save_interval": self.data.auto_save_interval
            },
            "presets": self._load_existing_presets()
        }
        
        try:
            # Ensure directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=4)
            
            get_logger().log(f"Configuration saved to {self.config_file}")
            
        except Exception as e:
            get_logger().log(f"Error saving config: {e}")
    
    def _load_existing_presets(self) -> Dict[str, Any]:
        """Load existing presets to preserve them during save."""
        if not self.config_file.exists():
            return {}
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get("presets", {})
        except Exception:
            return {}
    
    def validate_config(self) -> bool:
        """Validate current configuration."""
        issues = []
        
        # Validate data directory
        if not os.path.exists(self.data.base_dir):
            try:
                os.makedirs(self.data.base_dir, exist_ok=True)
            except Exception as e:
                issues.append(f"Cannot create data directory: {e}")
        
        # Validate Arduino IDs
        if not self.arduino.ids:
            issues.append("No Arduino IDs configured")
        
        # Log validation issues
        if issues:
            for issue in issues:
                get_logger().log(f"Config validation issue: {issue}")
            return False
        
        return True
    
    def get_arduino_id(self, hw_id: str) -> Optional[int]:
        """Get Arduino ID for hardware ID."""
        return self.arduino.get_arduino_id(hw_id)
    
    def set_arduino_id(self, hw_id: str, arduino_id: int) -> None:
        """Set Arduino ID and save configuration."""
        self.arduino.set_arduino_id(hw_id, arduino_id)
        self.save_config()
    
    def get_data_directory(self, trial_name: str = "") -> Path:
        """Get data directory for current trial."""
        return self.data.get_data_dir(trial_name)
