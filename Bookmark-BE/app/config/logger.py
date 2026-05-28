# Standard library imports

import os

import logging

from logging.handlers import TimedRotatingFileHandler

# Local application imports

from app.config.settings import app_settings

# Ensure the logs directory exists

LOG_DIR = "logs"

if not os.path.exists(LOG_DIR):

    os.makedirs(LOG_DIR)


def setup_logging():
    """

    Setup the logging configuration for the application.

    Configures weekly rotation and intercepts server/database logs.



    Returns:

        logger (logging.Logger): The configured application logger

    """

    logger = logging.getLogger(app_settings.LOGGER_NAME)

    # Prevent duplicate handlers

    if logger.hasHandlers():

        return logger

    logger.setLevel(logging.DEBUG)

    # Standard JSON Format

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # 1. Application Log Handler (Daily rotation, 7-day window)

    info_handler = TimedRotatingFileHandler(
        os.path.join(LOG_DIR, "info.log"),
        when="D",
        interval=app_settings.INTERVAL,
        backupCount=app_settings.LOG_BACKUP_COUNT,  # Keep app_settings.LOG_BACKUP_COUNT days of history
        encoding="utf-8",
    )

    info_handler.setLevel(logging.INFO)

    info_handler.setFormatter(formatter)

    # 2. Error Log Handler (Daily rotation)

    error_handler = TimedRotatingFileHandler(
        os.path.join(LOG_DIR, "error.log"),
        when="D",
        interval=app_settings.INTERVAL,
        backupCount=app_settings.LOG_BACKUP_COUNT,
        encoding="utf-8",
    )

    error_handler.setLevel(logging.ERROR)

    error_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()

    console_handler.setLevel(logging.DEBUG)  # or INFO

    console_handler.setFormatter(formatter)

    # Add handlers to the main application logger

    logger.addHandler(info_handler)

    logger.addHandler(error_handler)

    logger.addHandler(console_handler)

    return logger


# Initialize logger

logger = setup_logging()
