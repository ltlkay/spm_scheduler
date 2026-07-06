import os
import time
import random
from datetime import datetime, timezone
from celery import Celery
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

BROKER_URL = os.environ.get('CELERY_BROKER_URL', "redis://localhost:6379/0")
RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', "redis://localhost:6379/0")

SYNC_DB_URL = os.environ.get("DATABASE_URL",
            "postgresql+psycopg2://postgres:postgres@localhost:5432/spm_db")

celery_app = Celery("spm_scheduler",
                    broker=BROKER_URL, backend=RESULT_BACKEND)
sync_engine = create_engine(SYNC_DB_URL)

@celery_app.task(name="run_scan")
def run_scan(job_id: int):
    from app.models import ScanJob, ScanResult, JobStatus

    with Session(sync_engine) as db:
        job = db.get(ScanJob, job_id)
        if job is None:
            raise ValueError(f"Job {job_id} is not found")
        try:
            job.status = JobStatus.running
            db.commit()

            time.sleep(random.uniform(3,5))

            grid = [[random.uniform(0.0,10.0) for _ in range(10)] for _ in range(10)]
            scan_data = {
                "height_map": grid,
                "resolution_nm": job.parameters.get("resolution_nm", 1.0),
                "scan_size_um": job.parameters.get("scan_size_um", 10.0),
            }

            scan_result = ScanResult(job_id=job_id,data=scan_data)
            db.add(scan_result)

            job.status = JobStatus.complete
            db.commit()

        except Exception as exc:
            job.status = JobStatus.failed
            db.commit()
            raise exc

