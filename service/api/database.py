"""SQLite database operations for job tracking"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import contextmanager


DB_PATH = os.getenv('DATABASE_PATH', 'db/jobs.db')


@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    """Initialize the database with schema"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                operation TEXT NOT NULL,
                params TEXT NOT NULL,
                status TEXT NOT NULL,
                result TEXT,
                error TEXT,
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP NOT NULL,
                completed_at TIMESTAMP
            )
        ''')
        conn.commit()
    print(f"Database initialized at {DB_PATH}")


def save_job(job_id: str, operation: str, params: Dict[str, Any], status: str = 'pending') -> None:
    """Save a new job to the database"""
    with get_db() as conn:
        conn.execute('''
            INSERT INTO jobs (id, operation, params, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            job_id,
            operation,
            json.dumps(params),
            status,
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        conn.commit()


def update_job_status(job_id: str, status: str, result: Optional[Dict] = None, error: Optional[Dict] = None):
    """Update job status and optionally add result or error"""
    with get_db() as conn:
        if status in ['completed', 'failed']:
            conn.execute('''
                UPDATE jobs 
                SET status = ?, result = ?, error = ?, updated_at = ?, completed_at = ?
                WHERE id = ?
            ''', (
                status,
                json.dumps(result) if result else None,
                json.dumps(error) if error else None,
                datetime.now().isoformat(),
                datetime.now().isoformat(),
                job_id
            ))
        else:
            conn.execute('''
                UPDATE jobs 
                SET status = ?, updated_at = ?
                WHERE id = ?
            ''', (status, datetime.now().isoformat(), job_id))
        conn.commit()


def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    """Get a job by ID"""
    with get_db() as conn:
        row = conn.execute('SELECT * FROM jobs WHERE id = ?', (job_id,)).fetchone()
        if row:
            return {
                'id': row['id'],
                'operation': row['operation'],
                'params': json.loads(row['params']),
                'status': row['status'],
                'result': json.loads(row['result']) if row['result'] else None,
                'error': json.loads(row['error']) if row['error'] else None,
                'created_at': row['created_at'],
                'updated_at': row['updated_at'],
                'completed_at': row['completed_at']
            }
        return None


def get_all_jobs(limit: int = 100) -> List[Dict[str, Any]]:
    """Get all jobs, most recent first"""
    with get_db() as conn:
        rows = conn.execute('''
            SELECT * FROM jobs 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,)).fetchall()
        
        return [
            {
                'id': row['id'],
                'operation': row['operation'],
                'params': json.loads(row['params']),
                'status': row['status'],
                'created_at': row['created_at']
            }
            for row in rows
        ]


def get_job_stats() -> Dict[str, Any]:
    """Get job statistics"""
    with get_db() as conn:
        stats = conn.execute('''
            SELECT 
                status, 
                COUNT(*) as count
            FROM jobs 
            GROUP BY status
        ''').fetchall()
        
        return {row['status']: row['count'] for row in stats}