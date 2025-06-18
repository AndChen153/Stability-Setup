"""
Example usage of the improved architecture components.

This file demonstrates how to use the new core modules and services
for common operations in the Stability-Setup application.
"""
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from core.config_manager import ConfigManager
from core.application_state import ApplicationState, ApplicationStatus
from core.error_handler import ErrorHandler, get_error_handler
from core.thread_manager import get_thread_manager
from services.measurement_service import MeasurementService
from gui.trial_manager.preset_data_class import Preset, Trial
from constants import Mode


def example_configuration_management():
    """Example of using the ConfigManager."""
    print("=== Configuration Management Example ===")
    
    # Initialize configuration manager
    config_file = Path("userSettings.json")
    config = ConfigManager(config_file)
    
    # Access configuration values
    print(f"Email user: {config.email.user}")
    print(f"Email valid: {config.email.is_valid()}")
    print(f"Data directory: {config.data.base_dir}")
    print(f"Arduino IDs: {config.arduino.ids}")
    
    # Modify configuration
    config.set_arduino_id("ABC123", 1)
    config.ui.theme = "dark"
    
    # Save configuration
    config.save_config()
    print("Configuration saved successfully")
    
    # Validate configuration
    is_valid = config.validate_config()
    print(f"Configuration valid: {is_valid}")


def example_application_state():
    """Example of using ApplicationState."""
    print("\n=== Application State Example ===")
    
    # Initialize application state
    app_state = ApplicationState()
    
    # Check initial state
    print(f"Initial status: {app_state.status.value}")
    print(f"Is busy: {app_state.is_busy()}")
    
    # Update Arduino state
    app_state.update_arduino_state(
        connected_devices=["device1", "device2"],
        unknown_devices=[],
        initialization_successful=True
    )
    print(f"Arduino valid: {app_state.arduino.is_valid()}")
    print(f"Device count: {app_state.arduino.device_count}")
    
    # Create a mock preset and start measurement
    from gui.trial_manager.preset_data_class import Preset, Trial
    from constants import Mode, Constants
    
    trial = Trial(Mode.SCAN, Constants.params[Mode.SCAN])
    preset = Preset("Test Preset", [trial])
    
    success = app_state.start_measurement(preset)
    print(f"Measurement started: {success}")
    print(f"Current status: {app_state.status.value}")
    print(f"Measurement info: {app_state.get_measurement_info()}")


def example_error_handling():
    """Example of using ErrorHandler."""
    print("\n=== Error Handling Example ===")
    
    # Get error handler
    error_handler = get_error_handler()
    
    # Handle different types of errors
    error_handler.info("This is an info message", context="Example")
    error_handler.warning("This is a warning", context="Example")
    error_handler.error("This is an error", context="Example", show_dialog=False)
    
    # Handle exceptions
    try:
        raise ValueError("Example exception")
    except Exception as e:
        error_handler.handle_exception(e, context="Example operation")
    
    print("Error handling examples completed")


def example_thread_management():
    """Example of using ThreadManager."""
    print("\n=== Thread Management Example ===")
    
    # Get thread manager
    thread_manager = get_thread_manager()
    
    def sample_task(duration: float, task_name: str):
        """Sample task that simulates work."""
        import time
        print(f"Task {task_name} starting...")
        time.sleep(duration)
        print(f"Task {task_name} completed!")
        return f"Result from {task_name}"
    
    # Submit tasks
    task1_id = thread_manager.submit_task(
        sample_task, 1.0, "Task1",
        task_name="Sample Task 1"
    )
    
    task2_id = thread_manager.submit_task(
        sample_task, 0.5, "Task2",
        task_name="Sample Task 2"
    )
    
    print(f"Submitted tasks: {task1_id}, {task2_id}")
    print(f"Running tasks: {len(thread_manager.get_running_tasks())}")
    
    # Wait for tasks to complete
    try:
        result1 = thread_manager.wait_for_task(task1_id, timeout=2.0)
        result2 = thread_manager.wait_for_task(task2_id, timeout=2.0)
        print(f"Task results: {result1}, {result2}")
    except Exception as e:
        print(f"Error waiting for tasks: {e}")
    
    print(f"Active tasks after completion: {thread_manager.get_task_count()}")


def example_measurement_service():
    """Example of using MeasurementService."""
    print("\n=== Measurement Service Example ===")
    
    # Initialize components
    config = ConfigManager("userSettings.json")
    app_state = ApplicationState()
    measurement_service = MeasurementService(config, app_state)
    
    # Check if ready for measurement
    ready = measurement_service.is_ready_for_measurement()
    print(f"Ready for measurement: {ready}")
    
    # Get measurement status
    status = measurement_service.get_measurement_status()
    print(f"Measurement status: {status}")
    
    # Initialize Arduinos (this would normally connect to real hardware)
    print("Note: Arduino initialization would normally connect to hardware")
    # success = measurement_service.initialize_arduinos("test_trial")
    # print(f"Arduino initialization: {success}")


def example_with_error_handling_decorator():
    """Example of using the error handling decorator."""
    print("\n=== Error Handling Decorator Example ===")
    
    from core.error_handler import with_error_handling, ErrorSeverity
    
    error_handler = get_error_handler()
    
    @with_error_handling(error_handler, "Risky operation", ErrorSeverity.WARNING, "default_value")
    def risky_operation(should_fail: bool = False):
        """Example function that might fail."""
        if should_fail:
            raise RuntimeError("Operation failed as requested")
        return "Success!"
    
    # Test successful operation
    result1 = risky_operation(False)
    print(f"Successful operation result: {result1}")
    
    # Test failed operation
    result2 = risky_operation(True)
    print(f"Failed operation result: {result2}")


if __name__ == "__main__":
    """Run all examples."""
    print("Stability-Setup Architecture Examples")
    print("=" * 50)
    
    try:
        example_configuration_management()
        example_application_state()
        example_error_handling()
        example_thread_management()
        example_measurement_service()
        example_with_error_handling_decorator()
        
        print("\n" + "=" * 50)
        print("All examples completed successfully!")
        
    except Exception as e:
        print(f"Error running examples: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up thread manager
        from core.thread_manager import shutdown_thread_manager
        shutdown_thread_manager()
        print("Cleanup completed.")
