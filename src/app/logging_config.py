import logging
import sys

from uvicorn.config import LOGGING_CONFIG

# Route uvicorn log handlers to stdout for Railway
for _handler in LOGGING_CONFIG["handlers"].values():
    _handler["stream"] = "ext://sys.stdout"


def get_logger():
    """Return the uvicorn error logger for consistent log formatting."""
    return logging.getLogger("uvicorn.error")
