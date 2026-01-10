"""
Centralized Error Handling Module

Provides consistent error handling, logging, and user notification across the application.
"""
import traceback
from enum import Enum
from typing import Optional, Callable, Any
from dataclasses import dataclass
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QMessageBox, QWidget
from helper.global_helpers import get_logger


class ErrorSeverity(Enum):
    """Error severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ErrorInfo:
    """Error information container."""
    message: str
    severity: ErrorSeverity
    exception: Optional[Exception] = None
    context: Optional[str] = None
    
    def __str__(self) -> str:
        """String representation of error."""
        parts = [f"[{self.severity.value.upper()}]"]
        if self.context:
            parts.append(f"[{self.context}]")
        parts.append(self.message)
        return " ".join(parts)


class ErrorHandler(QObject):
    """
    Centralized error handler for the application.
    
    Provides consistent error handling, logging, and user notification.
    """
    
    error_occurred = Signal(ErrorInfo)
    
    def __init__(self, parent_widget: Optional[QWidget] = None):
        super().__init__()
        self.parent_widget = parent_widget
        self.show_dialogs = True
        
    def handle_error(self, 
                    message: str,
                    severity: ErrorSeverity = ErrorSeverity.ERROR,
                    exception: Optional[Exception] = None,
                    context: Optional[str] = None,
                    show_dialog: bool = True) -> None:
        """
        Handle an error with logging and optional user notification.
        
        Args:
            message: Error message
            severity: Error severity level
            exception: Optional exception object
            context: Optional context information
            show_dialog: Whether to show dialog to user
        """
        error_info = ErrorInfo(message, severity, exception, context)
        
        # Log the error
        self._log_error(error_info)
        
        # Show dialog if requested and enabled
        if show_dialog and self.show_dialogs:
            self._show_error_dialog(error_info)
        
        # Emit signal for other components
        self.error_occurred.emit(error_info)
    
    def _log_error(self, error_info: ErrorInfo) -> None:
        """Log error information."""
        logger = get_logger()
        
        # Log the main error message
        logger.log(str(error_info))
        
        # Log exception details if available
        if error_info.exception:
            logger.log(f"Exception type: {type(error_info.exception).__name__}")
            logger.log(f"Exception details: {str(error_info.exception)}")
            
            # Log traceback for errors and critical issues
            if error_info.severity in [ErrorSeverity.ERROR, ErrorSeverity.CRITICAL]:
                logger.log("Traceback:")
                for line in traceback.format_exception(
                    type(error_info.exception),
                    error_info.exception,
                    error_info.exception.__traceback__
                ):
                    logger.log(line.rstrip())
    
    def _show_error_dialog(self, error_info: ErrorInfo) -> None:
        """Show error dialog to user."""
        if not self.parent_widget:
            return
        
        # Map severity to QMessageBox icon
        icon_map = {
            ErrorSeverity.INFO: QMessageBox.Information,
            ErrorSeverity.WARNING: QMessageBox.Warning,
            ErrorSeverity.ERROR: QMessageBox.Critical,
            ErrorSeverity.CRITICAL: QMessageBox.Critical
        }
        
        # Create title
        title_map = {
            ErrorSeverity.INFO: "Information",
            ErrorSeverity.WARNING: "Warning",
            ErrorSeverity.ERROR: "Error",
            ErrorSeverity.CRITICAL: "Critical Error"
        }
        
        title = title_map.get(error_info.severity, "Error")
        if error_info.context:
            title = f"{title} - {error_info.context}"
        
        # Create message
        message = error_info.message
        if error_info.exception and error_info.severity in [ErrorSeverity.ERROR, ErrorSeverity.CRITICAL]:
            message += f"\n\nTechnical details: {str(error_info.exception)}"
        
        # Show dialog
        msg_box = QMessageBox(self.parent_widget)
        msg_box.setIcon(icon_map.get(error_info.severity, QMessageBox.Critical))
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec()
    
    def handle_exception(self, 
                        exception: Exception,
                        context: str = "",
                        severity: ErrorSeverity = ErrorSeverity.ERROR) -> None:
        """
        Handle an exception with automatic message generation.
        
        Args:
            exception: The exception to handle
            context: Context where the exception occurred
            severity: Error severity level
        """
        message = f"An error occurred: {str(exception)}"
        self.handle_error(message, severity, exception, context)
    
    def set_show_dialogs(self, show: bool) -> None:
        """Enable or disable error dialogs."""
        self.show_dialogs = show
    
    def info(self, message: str, context: str = "", show_dialog: bool = False) -> None:
        """Log an info message."""
        self.handle_error(message, ErrorSeverity.INFO, context=context, show_dialog=show_dialog)
    
    def warning(self, message: str, context: str = "", show_dialog: bool = True) -> None:
        """Log a warning message."""
        self.handle_error(message, ErrorSeverity.WARNING, context=context, show_dialog=show_dialog)
    
    def error(self, message: str, context: str = "", show_dialog: bool = True) -> None:
        """Log an error message."""
        self.handle_error(message, ErrorSeverity.ERROR, context=context, show_dialog=show_dialog)
    
    def critical(self, message: str, context: str = "", show_dialog: bool = True) -> None:
        """Log a critical error message."""
        self.handle_error(message, ErrorSeverity.CRITICAL, context=context, show_dialog=show_dialog)


def with_error_handling(error_handler: ErrorHandler, 
                       context: str = "",
                       severity: ErrorSeverity = ErrorSeverity.ERROR,
                       return_value: Any = None):
    """
    Decorator for automatic error handling in methods.
    
    Args:
        error_handler: ErrorHandler instance
        context: Context description
        severity: Error severity for caught exceptions
        return_value: Value to return on error
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_handler.handle_exception(e, context or func.__name__, severity)
                return return_value
        return wrapper
    return decorator


# Global error handler instance
_global_error_handler: Optional[ErrorHandler] = None


def get_error_handler() -> ErrorHandler:
    """Get the global error handler instance."""
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = ErrorHandler()
    return _global_error_handler


def set_error_handler(handler: ErrorHandler) -> None:
    """Set the global error handler instance."""
    global _global_error_handler
    _global_error_handler = handler
