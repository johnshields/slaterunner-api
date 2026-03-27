import logging
import sys

from uvicorn.config import LOGGING_CONFIG

# Route uvicorn log handlers to stdout for Railway
for _handler in LOGGING_CONFIG["handlers"].values():
    _handler["stream"] = "ext://sys.stdout"

# Quiet down noisy third-party loggers
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)


def get_logger():
    """Return the uvicorn error logger for consistent log formatting."""
    return logging.getLogger("uvicorn.error")
