import inspect

def custom_print(*args, **kwargs):
    """Custom print function with filename and line number."""
    caller_frame = inspect.stack()[1]
    filepath = caller_frame.filename
    filename = filepath.split("\\")[-1]

    line_number = caller_frame.lineno
    print(f"[{filename}:{line_number}]", *args, **kwargs)