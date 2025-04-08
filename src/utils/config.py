"""
This module contains functions for helping with configuration files.
It includes loading the configuration from a YAML file and setting up a logger.
"""

import os
import logging
import yaml


def load_config(file_path: str) -> dict:
    """
    Load the configuration file.

    Parameters:
        file_path - str: The path to the configuration file

    Returns:
        dict: The configuration data
    """
    with open(file_path, "r") as file:
        config = yaml.safe_load(file)
    return config


def get_logger(
    file_name: str = "app.log", level: int = logging.INFO
) -> logging.Logger:
    """
    Get a logger with the specified name and level.

    Parameters:
        file_name - str: Name of the log file
        level - int: Logging level

    Returns:
        logging.Logger: Logger object
    """
    # -- Get the logger configuration
    log_config = load_config("example_config.yaml")["LOGGING"]

    # -- Define the logger settings
    level = log_config.get("LEVEL", level)
    file_name = log_config.get("FILENAME", file_name)

    # -- Create file_name path if it doesn't exist
    if not os.path.exists(file_name):
        os.makedirs(os.path.dirname(file_name), exist_ok=True)

    # -- Create a logger
    logger = logging.getLogger("scrape_search")

    # -- Set the logging level
    logger.setLevel(level)

    # -- Check if handlers are already added
    if not logger.handlers:
        # -- Create a formatter
        formatter = logging.Formatter(
            "{asctime} - {levelname}: {message}", style="{", datefmt="%d-%m-%Y %H:%M:%S"
        )

        # -- Create a console handler
        ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(formatter)

        # -- Create a file handler
        fh = logging.FileHandler(file_name)
        fh.setLevel(level)
        fh.setFormatter(formatter)

        # -- Add the handlers to the logger
        if "console" in log_config.get("HANDLERS", []):
            logger.addHandler(ch)
        if "file" in log_config.get("HANDLERS", []):
            logger.addHandler(fh)

    return logger
