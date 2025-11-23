"""
Centralized logging configuration for KiiT AI Agents
"""
import logging
import sys
from pathlib import Path
from datetime import datetime

# Import config
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import LOGGING_CONFIG

def setup_logger(name: str, log_file: str = None) -> logging.Logger:
    """
    Set up a logger with consistent formatting across the application.

    Args:
        name: Name of the logger (typically __name__)
        log_file: Optional log file name (will be created in logs directory)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Only configure if not already configured
    if logger.handlers:
        return logger

    # Set level from config
    log_level = getattr(logging, LOGGING_CONFIG["level"].upper(), logging.INFO)
    logger.setLevel(log_level)

    # Create formatters
    formatter = logging.Formatter(LOGGING_CONFIG["format"])

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler if log_file is specified
    if log_file:
        log_dir = LOGGING_CONFIG["log_dir"]
        log_dir.mkdir(exist_ok=True)

        file_handler = logging.FileHandler(
            log_dir / f"{log_file}_{datetime.now().strftime('%Y%m%d')}.log"
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

# Example usage:
# from utils.logger import setup_logger
# logger = setup_logger(__name__, "bonafide")
# logger.info("Processing bonafide request")
# logger.error("Failed to process request", exc_info=True)
