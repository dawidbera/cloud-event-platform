import logging
import sys

def setup_logging():
    """Configures stdout-based standard logging for the service to ensure consistent log formatting."""
    # Simple structured logging using standard library
    # In production, consider structlog or similar json loggers
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

def get_logger(name: str) -> logging.Logger:
    """Returns a configured logger instance bound to the caller's module name."""
    return logging.getLogger(name)
