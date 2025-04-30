import inspect
from datetime import datetime

class Logger:
    def __init__(self):
        self.output_widget = None

    def set_output_widget(self, widget):
        self.output_widget = widget

    def log(self, *args, **kwargs):
        caller_frame = inspect.stack()[1]
        filepath = caller_frame.filename
        filename = filepath.split("\\")[-1]
        line_number = caller_frame.lineno

        # Add timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"[{timestamp}] [{filename}:{line_number}] " + " ".join(map(str, args))

        print(message, **kwargs)

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

logger = Logger()
