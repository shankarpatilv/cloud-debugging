"""System event logging functionality"""

import json
from datetime import datetime
from typing import Dict, Any

from . import LogLevel


class SystemLogger:
    def __init__(self, file_logger, log_store, LogType, cloudwatch=None):
        """Initialize system logger with backends"""
        self.file_logger = file_logger
        self.log_store = log_store
        self.LogType = LogType
        self.cloudwatch = cloudwatch
    
    def log_system_event(self,
                         event: str,
                         message: str,
                         level: str = LogLevel.INFO,
                         details: Dict = None):
        """Log system events"""
        
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'event': event,
            'message': message,
            'level': level
        }
        
        if details:
            log_data['details'] = details
        
        # Log to all backends
        if level == LogLevel.ERROR:
            self.file_logger.error(json.dumps(log_data))
        else:
            self.file_logger.info(json.dumps(log_data))
        
        self.log_store.log(
            log_type=self.LogType.SYSTEM_EVENT,
            level=level,
            event=event,
            message=message,
            details=details
        )
        
        if self.cloudwatch:
            self.cloudwatch.log(
                level=level,
                message=message,
                log_type="SYSTEM_EVENT",
                details=details
            )