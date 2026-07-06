import pytest
from unittest.mock import MagicMock, patch
from app.models import JobStatus

def make_job(job_id: int):
    job = MagicMock()
    job.id = job_id
    job.status = JobStatus.pending
    job.parameters = {"scan_size_um": 5.0, "resolution": 1.0}
    return job

@patch("app.tasks.Session")
@patch("app.tasks.time.sleep", return_value=None)
def test_run_scan_happy_path(mock_sleep, MockSession):
    job = make_job(1)
    db = MagicMock()
    db.get.return_value = job
    MockSession.return_value.__enter__.return_value = db

    from app.tasks import run_scan
    run_scan(1)

    assert job.status == JobStatus.complete
    assert db.add.called
    assert db.commit.call_count == 2

@patch("app.tasks.Session")
@patch("app.tasks.time.sleep", side_effect=RuntimeError("INstrument disconnected"))
def test_run_scan_failed_on_exception(mock_sleep, MockSession):
    job = make_job(1)
    db = MagicMock()
    db.get.return_value = job
    MockSession.return_value.__enter__.return_value = db

    from app.tasks import run_scan
    with pytest.raises(RuntimeError):
        run_scan(1)

    assert job.status == JobStatus.failed
    assert db.commit.call_count == 2