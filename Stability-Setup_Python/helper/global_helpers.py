# get_logger().py
import inspect
from datetime import datetime
from PySide6.QtCore import QObject, Signal


class Logger(QObject):
    log_signal = Signal(str)

    def __init__(self):
        super().__init__()
        self.output_widget = None
        self.log_signal.connect(self._append_message)

    def set_output_widget(self, widget):
        self.output_widget = widget

    def log(self, *args, **kwargs):
        caller_frame = inspect.stack()[1]
        filepath = caller_frame.filename
        filename = filepath.split("\\")[-1]
        line_number = caller_frame.lineno

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"[{timestamp}] [{filename}:{line_number}] " + " ".join(map(str, args))

        print(message, **kwargs)
        self.log_signal.emit(message)

    def _append_message(self, message):
        if self.output_widget:
            self.output_widget.append(message)
            self.output_widget.verticalScrollBar().setValue(
                self.output_widget.verticalScrollBar().maximum()
            )

    def clear(self):
        if self.output_widget:
            self.output_widget.clear()

    def save(self, path):
        if self.output_widget:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.output_widget.toPlainText())


# Global singleton instance
_logger_instance = None

def get_logger():
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = Logger()
    return _logger_instance
