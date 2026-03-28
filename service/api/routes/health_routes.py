"""Health check and system status endpoints"""

from fastapi import APIRouter
from datetime import datetime
import os

from ..models import HealthResponse
from ..job_processor import JobProcessor

router = APIRouter(tags=["health"])
processor = JobProcessor()
start_time = datetime.now()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    uptime = (datetime.now() - start_time).total_seconds()
    
    return HealthResponse(
        status="healthy",
        database=os.path.exists(os.getenv('DATABASE_PATH', 'db/jobs.db')),
        dataset_loaded=processor.df is not None,
        dataset_rows=len(processor.df),
        uptime_seconds=uptime
    )