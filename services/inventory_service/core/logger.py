import logging
import sys

def setup_logging():
    """Configures the root logger with a standard formatting string and outputs to stdout."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )

def get_logger(name: str) -> logging.Logger:
    """Retrieves a logger instance customized with the provided module name."""
    return logging.getLogger(name)
