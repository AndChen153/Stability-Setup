"""
Example usage of the refactored PresetQueueWidget.

This example demonstrates how to use the PresetQueueWidget with the new
ConfigManager architecture.
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from gui.trial_manager.preset_window_widget import PresetQueueWidget
from gui.trial_manager.preset_data_class import Preset, Trial
from constants import Mode, Constants
from core.config_manager import ConfigManager


class PresetWidgetExample(QMainWindow):
    """Example application showing PresetQueueWidget usage."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PresetQueueWidget Example")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create a test configuration file
        self.config_file = Path("example_config.json")
        self._create_example_config()
        
        # Create the preset widget
        self.preset_widget = PresetQueueWidget(str(self.config_file))
        
        # Connect signals
        self.preset_widget.run_start.connect(self.on_preset_start)
        
        # Set as central widget
        self.setCentralWidget(self.preset_widget)
        
        print("PresetQueueWidget Example Started")
        print("- Create presets using the left panel")
        print("- Add trials using the middle panel")
        print("- Edit trial parameters using the right panel")
        print("- Click 'Start' to run a preset")
    
    def _create_example_config(self):
        """Create an example configuration file with sample presets."""
        config_data = {
            "email_settings": {
                "user": "example@test.com",
                "pass": "example_password"
            },
            "arduino_ids": {
                "ABC123": 1,
                "DEF456": 2
            },
            "ui_settings": {
                "theme": "light",
                "window_geometry": {
                    "width": 1200,
                    "height": 800
                }
            },
            "data_settings": {
                "base_dir": str(Path.cwd() / "example_data"),
                "auto_save_interval": 20
            },
            "presets": {
                "example-preset-1": {
                    "trial_name": "Example Scan Preset",
                    "trial": [
                        {
                            "trial_type": "Scan",
                            "trial_id": "scan-trial-1",
                            "trial_params": {
                                "Scan Range (V)": "1.2",
                                "Scan Step Size (V)": "0.03",
                                "Scan Read Count": "5",
                                "Scan Rate (mV/s)": "50",
                                "Scan Mode": "1",
                                "Cell Area (mm^2)": "0.128"
                            }
                        }
                    ]
                },
                "example-preset-2": {
                    "trial_name": "Example MPPT Preset",
                    "trial": [
                        {
                            "trial_type": "Mppt",
                            "trial_id": "mppt-trial-1",
                            "trial_params": {
                                "Starting Voltage (V)": "0.50",
                                "Starting Voltage Multiplier (%)": "0.6",
                                "Step Size (V)": "0.001",
                                "Total Time": "60",
                                "Measurements Per Step": "100",
                                "Settling Time (ms)": "300",
                                "Measurement Interval (ms)": "200",
                                "Cell Area (mm^2)": "0.128",
                                "Time Param": "mins"
                            }
                        }
                    ]
                },
                "example-preset-3": {
                    "trial_name": "Mixed Preset",
                    "trial": [
                        {
                            "trial_type": "Scan",
                            "trial_id": "scan-trial-2",
                            "trial_params": {
                                "Scan Range (V)": "1.0",
                                "Scan Step Size (V)": "0.02",
                                "Scan Read Count": "3",
                                "Scan Rate (mV/s)": "30",
                                "Scan Mode": "0",
                                "Cell Area (mm^2)": "0.128"
                            }
                        },
                        {
                            "trial_type": "Mppt",
                            "trial_id": "mppt-trial-2",
                            "trial_params": {
                                "Starting Voltage (V)": "0.40",
                                "Starting Voltage Multiplier (%)": "0.7",
                                "Step Size (V)": "0.002",
                                "Total Time": "30",
                                "Measurements Per Step": "50",
                                "Settling Time (ms)": "200",
                                "Measurement Interval (ms)": "150",
                                "Cell Area (mm^2)": "0.128",
                                "Time Param": "mins"
                            }
                        }
                    ]
                }
            }
        }
        
        # Save example configuration
        import json
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=4)
        
        print(f"Created example configuration: {self.config_file}")
    
    def on_preset_start(self, preset: Preset):
        """Handle preset start signal."""
        print(f"\n=== PRESET START REQUESTED ===")
        print(f"Preset Name: {preset.name}")
        print(f"Number of Trials: {len(preset.trials)}")
        
        for i, trial in enumerate(preset.trials, 1):
            trial_type = Constants.run_modes[trial.trial_type]
            print(f"  Trial {i}: {trial_type}")
            print(f"    Parameters: {trial.params}")
        
        print("=== END PRESET INFO ===\n")
        
        # In a real application, this would start the measurement
        # For this example, we just print the information
    
    def closeEvent(self, event):
        """Clean up when closing the application."""
        # Remove example config file
        if self.config_file.exists():
            self.config_file.unlink()
            print(f"Cleaned up example configuration: {self.config_file}")
        
        event.accept()


def demonstrate_config_manager_integration():
    """Demonstrate how the widget integrates with ConfigManager."""
    print("\n=== ConfigManager Integration Demo ===")
    
    # Create a ConfigManager instance
    config_file = Path("demo_config.json")
    config_manager = ConfigManager(config_file)
    
    print(f"Config file: {config_manager.config_file}")
    print(f"Email valid: {config_manager.email.is_valid()}")
    print(f"Arduino IDs: {config_manager.arduino.ids}")
    print(f"Data directory: {config_manager.data.base_dir}")
    
    # The PresetQueueWidget would use this same ConfigManager
    print("PresetQueueWidget uses the same ConfigManager for consistency")
    
    # Clean up
    if config_file.exists():
        config_file.unlink()
    
    print("=== End Demo ===\n")


def demonstrate_error_handling():
    """Demonstrate improved error handling."""
    print("\n=== Error Handling Demo ===")
    
    from core.error_handler import get_error_handler
    
    error_handler = get_error_handler()
    
    # Simulate various error scenarios that the widget handles
    error_handler.info("Preset loaded successfully", context="PresetWidget")
    error_handler.warning("Unknown trial type found", context="PresetWidget")
    error_handler.error("Failed to save preset", context="PresetWidget", show_dialog=False)
    
    print("PresetQueueWidget uses centralized error handling for consistency")
    print("=== End Error Demo ===\n")


if __name__ == "__main__":
    """Run the PresetQueueWidget example."""
    
    # Demonstrate the architecture improvements
    demonstrate_config_manager_integration()
    demonstrate_error_handling()
    
    # Create and run the GUI example
    app = QApplication(sys.argv)
    
    try:
        window = PresetWidgetExample()
        window.show()
        
        print("GUI Example running...")
        print("Close the window to exit.")
        
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"Error running example: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("Example completed.")
