import datetime
import enum
import os
import logging
import pathlib
from typing import Dict, Optional
from pprint import pp


class LogType(enum.Enum):
    SUCCESS = "success"
    INFO = "info"
    ERROR = "error"
    CRITICAL = "critical"
    WARN = "warn"


class AuthLogger:
    """Logger class for authentication service with file-based logging."""

    _LEVEL_MAP: Dict[LogType, int] = {
        LogType.INFO: logging.INFO,
        LogType.WARN: logging.WARNING,
        LogType.SUCCESS: logging.INFO,
        LogType.ERROR: logging.ERROR,
        LogType.CRITICAL: logging.CRITICAL,
    }

    def __init__(self, name: str, log_level: int = logging.DEBUG):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)

        # Prevent duplicate handlers if logger already exists
        if self.logger.handlers:
            self.logger.handlers.clear()

        self.root_path = pathlib.Path(__file__).parent.parent
        self.log_dir = self.root_path / "logs"
        self.handlers: Dict[LogType, logging.FileHandler] = {}
        self._init_environment()

    def _init_environment(self) -> None:
        """Initialize logging environment and create handlers."""
        self.log_dir.mkdir(exist_ok=True)
        self.formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Create handlers for all log types
        for log_type in LogType:
            self._add_handler(log_type)

    def _add_handler(self, log_type: LogType) -> None:
        """Add a file handler for specific log type."""
        log_value = log_type.value
        handler_name = f"{datetime.date.today()}-{log_value}.log"
        log_path = self.log_dir / handler_name

        handler = logging.FileHandler(log_path, encoding='utf-8')
        handler.setLevel(self._LEVEL_MAP[log_type])
        handler.setFormatter(self.formatter)

        # Add filter to only log messages of this specific type
        handler.addFilter(lambda record: record.levelno == self._LEVEL_MAP[log_type])

        self.handlers[log_type] = handler
        self.logger.addHandler(handler)

    def log(self, log_type: LogType, message: str) -> None:
        """Log a message with specified log type."""
        if log_type not in self._LEVEL_MAP:
            raise ValueError(f"Invalid log type: {log_type}")

        level = self._LEVEL_MAP[log_type]
        self.logger.log(level, message)

    def success(self, message: str) -> None:
        """Log success message."""
        self.log(LogType.SUCCESS, message)

    def info(self, message: str) -> None:
        """Log info message."""
        self.log(LogType.INFO, message)

    def warning(self, message: str) -> None:
        """Log warning message."""
        self.log(LogType.WARN, message)

    def error(self, message: str) -> None:
        """Log error message."""
        self.log(LogType.ERROR, message)

    def critical(self, message: str) -> None:
        """Log critical message."""
        self.log(LogType.CRITICAL, message)

    def display_handlers(self) -> None:
        """Display current handlers information."""
        print("Active handlers:")
        for log_type, handler in self.handlers.items():
            print(f"  {log_type.name}: {handler.baseFilename}")

    def close(self) -> None:
        """Close all handlers properly."""
        for handler in self.handlers.values():
            handler.close()
        self.logger.handlers.clear()
        self.handlers.clear()


# Usage example
if __name__ == "__main__":
    # Create logger instance
    auth_logger = AuthLogger('auth-service')

    # Test logging
    auth_logger.info("Application started")
    auth_logger.success("User authentication successful")
    auth_logger.warning("Invalid login attempt")
    auth_logger.error("Database connection failed")
    auth_logger.critical("System is shutting down")

    # Display handler information
    auth_logger.display_handlers()

    # Proper cleanup
    auth_logger.close()