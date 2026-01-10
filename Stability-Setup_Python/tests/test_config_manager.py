"""
Unit tests for ConfigManager.

Demonstrates how the improved architecture enables better testing
by separating business logic from UI components.
"""
import unittest
import tempfile
import json
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from core.config_manager import ConfigManager, EmailConfig, ArduinoConfig


class TestConfigManager(unittest.TestCase):
    """Test cases for ConfigManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = Path(self.temp_dir) / "test_config.json"
        
        # Create test configuration data
        self.test_config_data = {
            "email_settings": {
                "user": "test@example.com",
                "pass": "test_password"
            },
            "arduino_ids": {
                "ABC123": 1,
                "DEF456": 2
            },
            "ui_settings": {
                "theme": "dark",
                "window_geometry": {
                    "width": 1024,
                    "height": 768
                }
            },
            "data_settings": {
                "base_dir": "/test/data",
                "auto_save_interval": 30
            }
        }
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_load_existing_config(self):
        """Test loading existing configuration file."""
        # Create config file
        with open(self.config_file, 'w') as f:
            json.dump(self.test_config_data, f)
        
        # Load configuration
        config = ConfigManager(self.config_file)
        
        # Verify email settings
        self.assertEqual(config.email.user, "test@example.com")
        self.assertEqual(config.email.password, "test_password")
        self.assertTrue(config.email.is_valid())
        
        # Verify Arduino settings
        self.assertEqual(config.arduino.get_arduino_id("ABC123"), 1)
        self.assertEqual(config.arduino.get_arduino_id("DEF456"), 2)
        self.assertIsNone(config.arduino.get_arduino_id("UNKNOWN"))
        
        # Verify UI settings
        self.assertEqual(config.ui.theme, "dark")
        self.assertEqual(config.ui.window_geometry["width"], 1024)
        
        # Verify data settings
        self.assertEqual(config.data.base_dir, "/test/data")
        self.assertEqual(config.data.auto_save_interval, 30)
    
    def test_create_default_config(self):
        """Test creation of default configuration."""
        # Load non-existent config file
        config = ConfigManager(self.config_file)
        
        # Verify defaults
        self.assertEqual(config.email.user, "")
        self.assertEqual(config.email.password, "")
        self.assertFalse(config.email.is_valid())
        
        self.assertEqual(config.arduino.ids, {})
        self.assertEqual(config.ui.theme, "light")
        
        # Verify config file was created
        self.assertTrue(self.config_file.exists())
    
    def test_save_config(self):
        """Test saving configuration."""
        config = ConfigManager(self.config_file)
        
        # Modify configuration
        config.email.user = "new@example.com"
        config.email.password = "new_password"
        config.arduino.set_arduino_id("NEW123", 3)
        config.ui.theme = "dark"
        
        # Save configuration
        config.save_config()
        
        # Load new instance and verify
        new_config = ConfigManager(self.config_file)
        self.assertEqual(new_config.email.user, "new@example.com")
        self.assertEqual(new_config.email.password, "new_password")
        self.assertEqual(new_config.arduino.get_arduino_id("NEW123"), 3)
        self.assertEqual(new_config.ui.theme, "dark")
    
    def test_arduino_id_management(self):
        """Test Arduino ID management."""
        config = ConfigManager(self.config_file)
        
        # Set Arduino IDs
        config.set_arduino_id("DEVICE1", 1)
        config.set_arduino_id("DEVICE2", 2)
        
        # Verify IDs
        self.assertEqual(config.get_arduino_id("DEVICE1"), 1)
        self.assertEqual(config.get_arduino_id("DEVICE2"), 2)
        self.assertIsNone(config.get_arduino_id("UNKNOWN"))
    
    def test_data_directory_generation(self):
        """Test data directory generation."""
        config = ConfigManager(self.config_file)
        config.data.base_dir = "/test/data"
        
        # Test without trial name
        data_dir = config.get_data_directory()
        self.assertTrue(str(data_dir).startswith("/test/data"))
        
        # Test with trial name
        data_dir_with_trial = config.get_data_directory("test_trial")
        self.assertIn("test_trial", str(data_dir_with_trial))
    
    def test_config_validation(self):
        """Test configuration validation."""
        config = ConfigManager(self.config_file)
        
        # Test with invalid data directory
        config.data.base_dir = "/invalid/path/that/does/not/exist"
        # Note: validation will try to create the directory
        # In a real test, you might want to mock os.makedirs
        
        # Test with no Arduino IDs
        config.arduino.ids = {}
        is_valid = config.validate_config()
        # Should be False due to no Arduino IDs
        self.assertFalse(is_valid)


class TestEmailConfig(unittest.TestCase):
    """Test cases for EmailConfig."""
    
    def test_valid_email_config(self):
        """Test valid email configuration."""
        email_config = EmailConfig("user@example.com", "password")
        self.assertTrue(email_config.is_valid())
    
    def test_invalid_email_config(self):
        """Test invalid email configurations."""
        # Empty user
        email_config1 = EmailConfig("", "password")
        self.assertFalse(email_config1.is_valid())
        
        # Empty password
        email_config2 = EmailConfig("user@example.com", "")
        self.assertFalse(email_config2.is_valid())
        
        # Both empty
        email_config3 = EmailConfig("", "")
        self.assertFalse(email_config3.is_valid())


class TestArduinoConfig(unittest.TestCase):
    """Test cases for ArduinoConfig."""
    
    def test_arduino_id_operations(self):
        """Test Arduino ID operations."""
        arduino_config = ArduinoConfig()
        
        # Test setting and getting IDs
        arduino_config.set_arduino_id("DEVICE1", 1)
        arduino_config.set_arduino_id("DEVICE2", 2)
        
        self.assertEqual(arduino_config.get_arduino_id("DEVICE1"), 1)
        self.assertEqual(arduino_config.get_arduino_id("DEVICE2"), 2)
        self.assertIsNone(arduino_config.get_arduino_id("UNKNOWN"))
        
        # Test overwriting ID
        arduino_config.set_arduino_id("DEVICE1", 10)
        self.assertEqual(arduino_config.get_arduino_id("DEVICE1"), 10)


if __name__ == "__main__":
    # Run the tests
    unittest.main(verbosity=2)
