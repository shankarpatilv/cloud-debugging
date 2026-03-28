"""Log analytics and metrics generation"""

import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any


class LogAnalytics:
    def __init__(self, db_path: str):
        """Initialize analytics with database path"""
        self.db_path = db_path
    
    def get_error_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get error summary for the last N hours"""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Count errors by type
            cursor = conn.execute("""
                SELECT error_type, COUNT(*) as count
                FROM logs
                WHERE level = 'ERROR' 
                AND timestamp >= ?
                AND error_type IS NOT NULL
                GROUP BY error_type
                ORDER BY count DESC
            """, (cutoff.isoformat(),))
            
            error_types = {row['error_type']: row['count'] for row in cursor}
            
            # Count failed jobs by operation
            cursor = conn.execute("""
                SELECT operation, COUNT(*) as count
                FROM logs
                WHERE status = 'failed'
                AND timestamp >= ?
                AND operation IS NOT NULL
                GROUP BY operation
                ORDER BY count DESC
            """, (cutoff.isoformat(),))
            
            failed_operations = {row['operation']: row['count'] for row in cursor}
            
            # Get total error count
            cursor = conn.execute("""
                SELECT COUNT(*) as total
                FROM logs
                WHERE level = 'ERROR'
                AND timestamp >= ?
            """, (cutoff.isoformat(),))
            
            total_errors = cursor.fetchone()['total']
            
            return {
                'total_errors': total_errors,
                'error_types': error_types,
                'failed_operations': failed_operations,
                'time_range_hours': hours
            }
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system performance metrics"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Average processing time by operation
            cursor = conn.execute("""
                SELECT operation, 
                       AVG(duration_ms) as avg_duration,
                       MIN(duration_ms) as min_duration,
                       MAX(duration_ms) as max_duration,
                       COUNT(*) as count
                FROM logs
                WHERE duration_ms IS NOT NULL
                AND operation IS NOT NULL
                GROUP BY operation
            """)
            
            performance = {}
            for row in cursor:
                performance[row['operation']] = {
                    'avg_ms': round(row['avg_duration'], 2),
                    'min_ms': row['min_duration'],
                    'max_ms': row['max_duration'],
                    'count': row['count']
                }
            
            return {
                'performance_by_operation': performance,
                'timestamp': datetime.now().isoformat()
            }