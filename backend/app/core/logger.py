import logging
import sys
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "component": record.name,
            "message": record.getMessage()
        }
        
        # Capture custom attributes if provided (e.g. execution metrics)
        if hasattr(record, "execution_time_ms"):
            log_record["execution_time_ms"] = record.execution_time_ms
        if hasattr(record, "success"):
            log_record["success"] = record.success
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
            
        return str(log_record)

def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        # Using a standard formatter for console readability, 
        # but could use JSONFormatter for production aggregation
        formatter = logging.Formatter(
            '%(asctime)s - [%(name)s] - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
    return logger
