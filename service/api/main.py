"""FastAPI application for data processing service"""

from fastapi import FastAPI
from datetime import datetime
import os

from .database import init_db
from .job_processor import JobProcessor
from .logging_config import setup_logging
from .routes.job_routes import router as job_router
from .routes.log_routes import router as log_router
from .routes.health_routes import router as health_router


# Initialize FastAPI app
app = FastAPI(
    title="Data Processing Service",
    description="Process pandas operations on dataset with job tracking",
    version="1.0.0"
)

# Initialize components
logger = setup_logging()
processor = JobProcessor()
start_time = datetime.now()

# Include routers
app.include_router(job_router)
app.include_router(log_router)
app.include_router(health_router)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()
    logger.info({
        'event': 'service_started',
        'dataset_rows': len(processor.df),
        'dataset_columns': len(processor.columns)
    })