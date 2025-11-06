"""
Logging configuration and utilities
Provides structured logging with rotation and different levels
"""

import os
import sys
from pathlib import Path
from loguru import logger
from datetime import datetime

# Create logs directory if it doesn't exist
LOGS_DIR = Path(__file__).parent.parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

def setup_logging():
    """Configure loguru logger with file rotation and formatting"""
    
    # Remove default handler
    logger.remove()
    
    # Console handler with colored output
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=os.getenv("LOG_LEVEL", "INFO"),
        colorize=True
    )
    
    # File handler for all logs
    logger.add(
        LOGS_DIR / "pipeline_{time:YYYY-MM-DD}.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="1 day",
        retention="30 days",
        compression="zip"
    )
    
    # Error file handler for error and critical logs
    logger.add(
        LOGS_DIR / "errors_{time:YYYY-MM-DD}.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        rotation="1 day",
        retention="90 days",
        compression="zip"
    )
    
    return logger

def get_logger(name: str = None):
    """Get a logger instance"""
    if not hasattr(get_logger, '_initialized'):
        setup_logging()
        get_logger._initialized = True
    
    return logger.bind(name=name) if name else logger

# Performance logging decorator
def log_execution_time(func):
    """Decorator to log function execution time"""
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        logger = get_logger(func.__module__)
        
        try:
            logger.info(f"Starting execution of {func.__name__}")
            result = func(*args, **kwargs)
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"Completed {func.__name__} in {execution_time:.2f} seconds")
            return result
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Failed {func.__name__} after {execution_time:.2f} seconds: {str(e)}")
            raise
    
    return wrapper