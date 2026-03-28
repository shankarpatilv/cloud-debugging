"""Log reading and query operations"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from .log_writer import LogType


class LogReader:
    def __init__(self, db_path: str):
        """Initialize log reader with database path"""
        self.db_path = db_path
    
    def query_logs(self, 
                   log_type: Optional[LogType] = None,
                   job_id: Optional[str] = None,
                   level: Optional[str] = None,
                   status: Optional[str] = None,
                   hours_ago: Optional[int] = None,
                   limit: int = 100) -> List[Dict]:
        """Query logs with filters"""
        query = "SELECT * FROM logs WHERE 1=1"
        params = []
        
        if log_type:
            query += " AND log_type = ?"
            params.append(log_type)
        
        if job_id:
            query += " AND job_id = ?"
            params.append(job_id)
        
        if level:
            query += " AND level = ?"
            params.append(level)
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        if hours_ago:
            cutoff = datetime.now() - timedelta(hours=hours_ago)
            query += " AND timestamp >= ?"
            params.append(cutoff.isoformat())
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            
            results = []
            for row in rows:
                log_entry = dict(row)
                if log_entry.get('details'):
                    log_entry['details'] = json.loads(log_entry['details'])
                results.append(log_entry)
            
            return results
    
    def get_job_timeline(self, job_id: str) -> List[Dict]:
        """Get complete timeline of events for a job"""
        logs = self.query_logs(job_id=job_id, limit=1000)
        return sorted(logs, key=lambda x: x['timestamp'])