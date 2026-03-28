"""Job event logging functionality"""

import json
from datetime import datetime
from typing import Dict, Any, Optional

from . import LogLevel


class JobLogger:
    def __init__(self, file_logger, log_store, LogType, cloudwatch=None):
        """Initialize job logger with backends"""
        self.file_logger = file_logger
        self.log_store = log_store
        self.LogType = LogType
        self.cloudwatch = cloudwatch
    
    def log_job_event(self,
                      event: str,
                      job_id: str,
                      operation: str = None,
                      status: str = None,
                      level: str = LogLevel.INFO,
                      error: Dict = None,
                      details: Dict = None,
                      duration_ms: float = None):
        """Log a job-related event to all backends"""
        
        # Prepare log data
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'event': event,
            'job_id': job_id,
            'operation': operation,
            'status': status,
            'level': level
        }
        
        if error:
            log_data['error'] = error
        if details:
            log_data['details'] = details
        if duration_ms:
            log_data['duration_ms'] = duration_ms
        
        # 1. Log to file
        if level == LogLevel.ERROR:
            self.file_logger.error(json.dumps(log_data))
        else:
            self.file_logger.info(json.dumps(log_data))
        
        # 2. Log to SQLite
        self.log_store.log(
            log_type=self.LogType.JOB_EVENT,
            level=level,
            event=event,
            job_id=job_id,
            operation=operation,
            status=status,
            error_type=error.get('type') if error else None,
            message=error.get('message') if error else None,
            details=details,
            duration_ms=duration_ms
        )
        
        # 3. Log to CloudWatch (if enabled)
        if self.cloudwatch:
            self.cloudwatch.log(
                level=level,
                message=f"{event}: {job_id}",
                log_type="JOB_EVENT",
                job_id=job_id,
                operation=operation,
                status=status,
                error_type=error.get('type') if error else None,
                details={**details, **({'error': error} if error else {})},
                duration_ms=duration_ms
            )
    
    def get_job_logs(self, job_id: str) -> list:
        """Get all logs for a specific job"""
        return self.log_store.query_logs(job_id=job_id)