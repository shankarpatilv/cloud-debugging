"""Log store wrapper that imports from storage modules"""

import os
import sqlite3
from .storage.log_writer import LogWriter
from .storage.log_reader import LogReader
from .storage.log_analytics import LogAnalytics


class LogStore:
    def __init__(self, db_path: str = "logs/logs.db"):
        """Initialize log store with all components"""
        # Create logs directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize database schema
        self._init_database(db_path)
        
        self.writer = LogWriter(db_path)
        self.reader = LogReader(db_path)
        self.analytics = LogAnalytics(db_path)
    
    def _init_database(self, db_path: str):
        """Initialize the database schema"""
        with sqlite3.connect(db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    log_type TEXT,
                    level TEXT,
                    event TEXT,
                    job_id TEXT,
                    operation TEXT,
                    status TEXT,
                    error_type TEXT,
                    message TEXT,
                    details TEXT,
                    duration_ms REAL
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_job_id ON logs(job_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON logs(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_log_type ON logs(log_type)")
            conn.commit()
    
    def log(self, *args, **kwargs):
        """Write a log entry"""
        return self.writer.log(*args, **kwargs)
    
    def query_logs(self, *args, **kwargs):
        """Query logs"""
        return self.reader.query_logs(*args, **kwargs)
    
    def get_error_summary(self, *args, **kwargs):
        """Get error summary"""
        return self.analytics.get_error_summary(*args, **kwargs)
    
    def get_job_timeline(self, *args, **kwargs):
        """Get job timeline"""
        return self.reader.get_job_timeline(*args, **kwargs)
    
    def get_system_metrics(self):
        """Get system metrics"""
        print(f"DEBUG log_store.get_system_metrics: calling analytics.get_system_metrics()")
        try:
            result = self.analytics.get_system_metrics()
            print(f"DEBUG log_store.get_system_metrics: returned {result}")
            return result
        except Exception as e:
            print(f"ERROR in log_store.get_system_metrics: {e}")
            raise


# Global instance
log_store = LogStore()