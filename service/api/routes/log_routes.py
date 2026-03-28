"""Log query API endpoints"""

from fastapi import APIRouter, HTTPException
from typing import Optional
import os

from ..log_store import log_store
from ..structured_logger import structured_logger

router = APIRouter(prefix="/logs", tags=["logs"])


@router.get("")
async def get_logs(job_id: Optional[str] = None, limit: int = 50):
    """Get recent logs (for debugging)"""
    log_path = os.getenv('LOG_PATH', 'logs/app.log')
    
    if not os.path.exists(log_path):
        return {"logs": []}
    
    logs = []
    with open(log_path, 'r') as f:
        for line in f:
            try:
                log_entry = eval(line)  # Parse JSON log
                if job_id and log_entry.get('job_id') != job_id:
                    continue
                logs.append(log_entry)
                if len(logs) >= limit:
                    break
            except:
                continue
    
    return {"logs": logs[-limit:]}


@router.get("/structured")
async def get_structured_logs(
    job_id: Optional[str] = None,
    log_type: Optional[str] = None,
    level: Optional[str] = None,
    hours: int = 1,
    limit: int = 100
):
    """Get structured logs with filtering"""
    try:
        print(f"DEBUG: /logs/structured called with job_id={job_id}, log_type={log_type}, level={level}, hours={hours}, limit={limit}")
        logs = log_store.query_logs(
            log_type=log_type,
            job_id=job_id,
            level=level,
            hours_ago=hours,
            limit=limit
        )
        print(f"DEBUG: query_logs returned {len(logs) if logs else 0} logs")
        return {
            "count": len(logs),
            "filters": {
                "job_id": job_id,
                "log_type": log_type,
                "level": level,
                "hours": hours
            },
            "logs": logs
        }
    except Exception as e:
        print(f"ERROR in /logs/structured: {e}")
        print(f"ERROR type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        raise


@router.get("/errors")
async def get_error_summary(hours: int = 24):
    """Get error summary and patterns"""
    summary = structured_logger.get_recent_errors(hours)
    return summary


@router.get("/metrics")
async def get_performance_metrics():
    """Get system performance metrics"""
    try:
        print(f"DEBUG: Calling structured_logger.get_system_metrics()")
        metrics = structured_logger.get_system_metrics()
        print(f"DEBUG: Metrics returned: {metrics}")
        return metrics
    except Exception as e:
        print(f"ERROR in /logs/metrics: {e}")
        print(f"ERROR type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        raise


@router.get("/timeline/{job_id}")
async def get_job_timeline(job_id: str):
    """Get complete timeline of events for a specific job"""
    timeline = log_store.get_job_timeline(job_id)
    if not timeline:
        raise HTTPException(status_code=404, detail="No logs found for this job")
    
    return {
        "job_id": job_id,
        "event_count": len(timeline),
        "timeline": timeline
    }