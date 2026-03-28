"""Job-related API endpoints"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
import uuid

from ..models import JobRequest
from ..database import save_job, get_job, get_all_jobs, get_job_stats
from ..structured_logger import structured_logger
from ..background.job_processor_task import process_job

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=dict)
async def create_job(request: JobRequest, background_tasks: BackgroundTasks):
    """Submit a new processing job"""
    job_id = str(uuid.uuid4())
    
    # Save job to database
    save_job(job_id, request.operation, request.params)
    
    # Log job creation with structured logger
    structured_logger.log_job_event(
        event='job_created',
        job_id=job_id,
        operation=request.operation,
        status='pending',
        level='INFO',
        details={'params': request.params}
    )
    
    # Process job in background
    background_tasks.add_task(process_job, job_id, request.operation, request.params)
    
    return {
        "job_id": job_id,
        "status": "pending",
        "message": "Job submitted successfully"
    }


@router.get("/{job_id}")
async def get_job_status(job_id: str):
    """Get status and result of a specific job"""
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.get("", response_model=List[dict])
async def list_jobs(limit: int = 100):
    """List all jobs"""
    return get_all_jobs(limit=limit)


@router.get("/statistics/summary")
async def get_statistics():
    """Get job statistics"""
    stats = get_job_stats()
    return {
        "statistics": stats,
        "total": sum(stats.values()),
        "success_rate": stats.get('completed', 0) / max(sum(stats.values()), 1) * 100
    }