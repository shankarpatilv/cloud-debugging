"""Log writing operations to SQLite"""

import json
import sqlite3
from typing import Dict, Optional
from enum import Enum


class LogType(str, Enum):
    JOB_EVENT = "job_event"
    API_REQUEST = "api_request"
    SYSTEM_EVENT = "system_event"
    ERROR = "error"
    PERFORMANCE = "performance"


class LogWriter:
    def __init__(self, db_path: str):
        """Initialize log writer with database path"""
        self.db_path = db_path
    
    def log(self, log_type: LogType, level: str, event: str = None, 
            job_id: str = None, operation: str = None, status: str = None,
            error_type: str = None, message: str = None, 
            details: Dict = None, duration_ms: float = None):
        """Write a structured log entry"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO logs 
                (log_type, level, event, job_id, operation, status, 
                 error_type, message, details, duration_ms)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                log_type, level, event, job_id, operation, status,
                error_type, message, 
                json.dumps(details) if details else None,
                duration_ms
            ))
            conn.commit()