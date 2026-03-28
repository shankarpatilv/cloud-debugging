"""API request logging functionality"""

import json
from datetime import datetime
from typing import Dict, Any

from . import LogLevel


class ApiLogger:
    def __init__(self, file_logger, log_store, LogType, cloudwatch=None):
        """Initialize API logger with backends"""
        self.file_logger = file_logger
        self.log_store = log_store
        self.LogType = LogType
        self.cloudwatch = cloudwatch
    
    def log_api_request(self,
                        method: str,
                        path: str,
                        status_code: int,
                        duration_ms: float,
                        details: Dict = None):
        """Log API request"""
        
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'method': method,
            'path': path,
            'status_code': status_code,
            'duration_ms': duration_ms
        }
        
        if details:
            log_data.update(details)
        
        # Log to all backends
        self.file_logger.info(json.dumps(log_data))
        
        self.log_store.log(
            log_type=self.LogType.API_REQUEST,
            level=LogLevel.INFO,
            event="api_request",
            message=f"{method} {path} - {status_code}",
            details=log_data,
            duration_ms=duration_ms
        )
        
        if self.cloudwatch:
            self.cloudwatch.log(
                level=LogLevel.INFO,
                message=f"{method} {path} - {status_code}",
                log_type="API_REQUEST",
                details=log_data,
                duration_ms=duration_ms
            )