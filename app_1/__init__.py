

from utils.colored_logger import ColoredLogger
import logging

from app.model import Model

from utils.prompt_loader import load_prompt, load_file


# Exceptions
exc = ColoredLogger(name="Exception", level=logging.DEBUG)
def log_error(instance, error):
    """
    Logs error with class name prefix.
    """
    exc.error(f"Error [{instance.__class__.__name__}] -> {error}")

