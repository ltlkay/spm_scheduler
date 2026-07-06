from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import ScanJob, JobStatus
from app.schemas import ScanJobCreate, ScanJobResponse, ScanResultResponse


router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.post("", response_model=ScanJobResponse, status_code=201)
async def create_job(payload: ScanJobCreate, db: AsyncSession = Depends(get_db)):
    from app.tasks import run_scan
    job = ScanJob(parameters=payload.parameters)
    db.add(job)
    await db.commit()
    await db.refresh(job)
    run_scan.delay(job.id)
    return job

@router.get("/{job_id}", response_model=ScanJobResponse, status_code=200)
async def get_job_status(job_id: int, db: AsyncSession = Depends(get_db)):
    job = await db.get(ScanJob, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.get("/{job_id}/result", response_model=ScanResultResponse, status_code=200)
async def get_job_result(job_id: int, db: AsyncSession = Depends(get_db)):
    from app.models import ScanResult
    job = await db.get(ScanJob, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status in (JobStatus.running, JobStatus.pending):
        raise HTTPException(status_code=404,
                            detail=f"Result is not ready - job is {job.status}")
    elif job.status is JobStatus.failed:
        raise HTTPException(status_code=409)
    result = (await db.scalar(select(ScanResult).where(ScanResult.job_id == job_id)))
    return result

@router.get("", response_model=list[ScanJobResponse])
async def list_jobs(status: JobStatus | None = None, db: AsyncSession = Depends(get_db)):
    stmt = select(ScanJob)
    if status is not None:
        stmt = stmt.where(ScanJob.status == status)
    results = (await db.scalars(stmt)).all()
    return results