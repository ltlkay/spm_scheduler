import enum
from datetime import datetime, timezone
from sqlalchemy import Enum, JSON, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.base import Base

class JobStatus(str, enum.Enum):
    pending = 'pending'
    running = 'running'
    complete = 'complete'
    failed = 'failed'

class ScanJob(Base):
    __tablename__ = "scan_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus, name="jobstatus"), default=JobStatus.pending, nullable=False
    )
    parameters: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    result: Mapped["ScanResult"]= relationship("ScanResult",
                                               back_populates="job", uselist=False)

class ScanResult(Base):
    __tablename__ = "scan_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("scan_jobs.id"), nullable=False, unique=True)
    data: Mapped[dict] = mapped_column(JSON)
    acquired_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    job: Mapped["ScanJob"] = relationship("ScanJob", back_populates="result")