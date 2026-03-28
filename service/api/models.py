"""Pydantic models for API requests and responses"""

from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from enum import Enum
from datetime import datetime


class OperationType(str, Enum):
    filter = "filter"
    select = "select"
    groupby = "groupby"
    sort = "sort"


class JobStatus(str, Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


class JobRequest(BaseModel):
    operation: OperationType
    params: Dict[str, Any]


class JobResponse(BaseModel):
    job_id: str
    status: JobStatus
    operation: OperationType
    params: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None


class JobSummary(BaseModel):
    job_id: str
    operation: OperationType
    status: JobStatus
    created_at: datetime


class HealthResponse(BaseModel):
    status: str
    database: bool
    dataset_loaded: bool
    dataset_rows: int
    uptime_seconds: float