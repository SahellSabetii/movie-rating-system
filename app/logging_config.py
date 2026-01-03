import logging
import logging.config
import json
import sys
from datetime import datetime
from typing import Dict, Any
from pathlib import Path


class JsonFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "service": "movie_rating_system",
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        if hasattr(record, 'extra'):
            log_data.update(record.extra)
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
            log_data["stack_trace"] = self.formatStack(record.stack_info) if record.stack_info else None
        
        return json.dumps(log_data, ensure_ascii=False)


def setup_logging(env: str = "development"):
    """Setup logging configuration based on environment"""
    
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    if env == "production":
        level = logging.INFO
        json_format = True
    else:
        level = logging.DEBUG
        json_format = False
    
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    root_logger.setLevel(level)
    
    file_handler = logging.FileHandler(
        log_dir / "movie.log",
        encoding='utf-8'
    )
    
    if json_format:
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    module_logger = logging.getLogger("movie")
    module_logger.setLevel(level)

    module_logger.info(f"Logging initialized. Environment: {env}")
    module_logger.info(f"Log file: {log_dir / 'movie.log'}")
    
    return module_logger


def get_logger(name: str = "movie"):
    """Get a logger instance with the given name"""
    return logging.getLogger(name)
