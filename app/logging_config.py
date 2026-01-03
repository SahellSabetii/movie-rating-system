import logging
import logging.config
import json
import sys
from datetime import datetime
from typing import Dict, Any


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
    
    if env == "production":
        level = logging.INFO
        json_format = True
    else:
        level = logging.DEBUG
        json_format = False
    
    logging.getLogger().handlers.clear()
    
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    console_handler = logging.StreamHandler(sys.stdout)
    
    if json_format:
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    module_logger = logging.getLogger("movie_rating")
    module_logger.setLevel(level)
    
    return module_logger

def get_logger(name: str = "movie_rating"):
    """Get a logger instance with the given name"""
    return logging.getLogger(name)
