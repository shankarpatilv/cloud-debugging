"""Structured logger wrapper that imports from logger modules"""

import os
import logging
from .logging_config import setup_logging
from .log_store import log_store, LogStore
from .storage.log_writer import LogType


class StructuredLogger:
    def __init__(self):
        """Initialize all logger components"""
        # Setup file logger
        self.file_logger = setup_logging()
        self.log_store = log_store
        self.LogType = LogType
        
        # Initialize loggers with dependencies
        from .loggers.job_logger import JobLogger
        from .loggers.api_logger import ApiLogger
        from .loggers.system_logger import SystemLogger
        
        self.job_logger = JobLogger(self.file_logger, self.log_store, LogType, None)
        self.api_logger = ApiLogger(self.file_logger, self.log_store, LogType, None)
        self.system_logger = SystemLogger(self.file_logger, self.log_store, LogType, None)
    
    def log_job_event(self, *args, **kwargs):
        """Log job events"""
        return self.job_logger.log_job_event(*args, **kwargs)
    
    def log_api_request(self, *args, **kwargs):
        """Log API requests"""
        return self.api_logger.log_api_request(*args, **kwargs)
    
    def log_system_event(self, *args, **kwargs):
        """Log system events"""
        return self.system_logger.log_system_event(*args, **kwargs)
    
    def get_recent_errors(self, hours: int = 1):
        """Get recent errors from log store"""
        return self.log_store.get_error_summary(hours)
    
    def get_system_metrics(self):
        """Get system metrics from log store"""
        return self.log_store.get_system_metrics()


# Global instance
structured_logger = StructuredLogger()