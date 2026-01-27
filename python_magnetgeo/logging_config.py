#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Logging configuration for python_magnetgeo package.

This module provides a centralized logging configuration for the entire package.
It supports multiple handlers (console, file) and customizable log levels.

Usage:
    # Get logger in any module
    from python_magnetgeo.logging_config import get_logger
    logger = get_logger(__name__)
    
    # Configure logging (typically done once at application startup)
    from python_magnetgeo.logging_config import configure_logging
    configure_logging(level='DEBUG', log_file='magnetgeo.log')
    
    # Use logger
    logger.info("Processing geometry data")
    logger.debug("Detailed debug information")
    logger.warning("Something unexpected happened")
    logger.error("An error occurred", exc_info=True)
"""

import logging
import sys
from pathlib import Path
from typing import Optional, Union


# Default format for log messages
DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DETAILED_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
SIMPLE_FORMAT = "%(levelname)s - %(name)s - %(message)s"

# Package logger name
PACKAGE_NAME = "python_magnetgeo"

# Store configuration state
_configured = False
_log_level = logging.INFO
_handlers = []


def get_logger(name: str = PACKAGE_NAME) -> logging.Logger:
    """
    Get a logger instance for the specified module.
    
    This is the primary interface for getting loggers throughout the package.
    Each module should call this with __name__ to get its own logger.
    
    Args:
        name: Logger name, typically __name__ of the calling module
        
    Returns:
        Logger instance configured for the package
        
    Example:
        >>> from python_magnetgeo.logging_config import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("Module initialized")
    """
    logger = logging.getLogger(name)
    
    # If not configured yet, use basic configuration
    if not _configured:
        configure_logging()
    
    return logger


def configure_logging(
    level: Union[str, int] = logging.INFO,
    log_file: Optional[Union[str, Path]] = None,
    log_format: str = DEFAULT_FORMAT,
    console: bool = True,
    file_level: Optional[Union[str, int]] = None,
    console_level: Optional[Union[str, int]] = None,
    propagate: bool = True,
) -> None:
    """
    Configure logging for the python_magnetgeo package.
    
    This should typically be called once at application startup. It sets up
    handlers for console and/or file logging with appropriate formatters.
    
    Args:
        level: Default logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file. If provided, enables file logging
        log_format: Format string for log messages. Options:
                   - DEFAULT_FORMAT: timestamp, name, level, message
                   - DETAILED_FORMAT: adds function name and line number
                   - SIMPLE_FORMAT: just level, name, message
                   - Custom format string
        console: Enable console (stderr) logging
        file_level: Logging level for file handler (defaults to 'level')
        console_level: Logging level for console handler (defaults to 'level')
        propagate: Whether to propagate logs to parent loggers
        
    Example:
        >>> # Basic configuration - console only at INFO level
        >>> configure_logging()
        
        >>> # Debug to console and file
        >>> configure_logging(level='DEBUG', log_file='app.log')
        
        >>> # Different levels for console and file
        >>> configure_logging(
        ...     console_level='INFO',
        ...     file_level='DEBUG',
        ...     log_file='debug.log'
        ... )
    """
    global _configured, _log_level, _handlers
    
    # Convert string levels to logging constants
    if isinstance(level, str):
        level = getattr(logging, level.upper())
    if file_level is not None and isinstance(file_level, str):
        file_level = getattr(logging, file_level.upper())
    if console_level is not None and isinstance(console_level, str):
        console_level = getattr(logging, console_level.upper())
    
    # Set default levels if not specified
    if file_level is None:
        file_level = level
    if console_level is None:
        console_level = level
    
    _log_level = level
    
    # Get the root logger for this package
    logger = logging.getLogger(PACKAGE_NAME)
    logger.setLevel(logging.DEBUG)  # Set to DEBUG to allow handlers to filter
    logger.propagate = propagate
    
    # Remove existing handlers to avoid duplicates on reconfiguration
    for handler in _handlers:
        logger.removeHandler(handler)
    _handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(log_format)
    
    # Add console handler if requested
    if console:
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(console_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        _handlers.append(console_handler)
    
    # Add file handler if log_file is specified
    if log_file:
        log_path = Path(log_file)
        # Create parent directories if they don't exist
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_path, mode='a')
        file_handler.setLevel(file_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        _handlers.append(file_handler)
    
    _configured = True
    
    # Log that logging has been configured
    logger.debug(f"Logging configured: level={logging.getLevelName(level)}, "
                f"console={console}, log_file={log_file}")


def set_level(level: Union[str, int], logger_name: Optional[str] = None) -> None:
    """
    Change logging level for package or specific logger.
    
    Args:
        level: New logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        logger_name: Optional specific logger name. If None, sets package level
        
    Example:
        >>> # Set package level to DEBUG
        >>> set_level('DEBUG')
        
        >>> # Set specific module to WARNING
        >>> set_level('WARNING', 'python_magnetgeo.utils')
    """
    if isinstance(level, str):
        level = getattr(logging, level.upper())
    
    if logger_name:
        logger = logging.getLogger(logger_name)
    else:
        logger = logging.getLogger(PACKAGE_NAME)
    
    logger.setLevel(level)
    
    # Also update handlers if setting package level
    if not logger_name or logger_name == PACKAGE_NAME:
        for handler in _handlers:
            handler.setLevel(level)


def disable_logging() -> None:
    """
    Disable all logging from the package.
    
    Useful for testing or when you want complete silence.
    """
    logger = logging.getLogger(PACKAGE_NAME)
    logger.disabled = True


def enable_logging() -> None:
    """
    Re-enable logging after it was disabled.
    """
    logger = logging.getLogger(PACKAGE_NAME)
    logger.disabled = False


def get_log_level() -> int:
    """
    Get current logging level.
    
    Returns:
        Current logging level constant (e.g., logging.INFO)
    """
    return _log_level


def is_configured() -> bool:
    """
    Check if logging has been configured.
    
    Returns:
        True if configure_logging has been called
    """
    return _configured


# Convenience aliases for common log levels
DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL
