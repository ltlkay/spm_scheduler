from datetime import datetime
from typing import Any
from pydantic import BaseModel
from app.models import JobStatus

class ScanJobCreate(BaseModel):
    parameters: dict[str, Any]

class ScanJobResponse(BaseModel):
    id: int
    status: JobStatus
    created_at: datetime

    model_config = {"from_attributes": True}

class ScanResultResponse(BaseModel):
    job_id: int
    data: dict[str, Any]
    acquired_at: datetime

    model_config = {"from_attributes": True}