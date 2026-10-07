# SPM Job Scheduler

[![CI](https://github.com/ltlkay/spm_scheduler/actions/workflows/ci.yml/badge.svg)](https://github.com/ltlkay/spm_scheduler/actions/workflows/ci.yml)

A backend service that simulates an instrument-control job pipeline. Researchers submit scan jobs through a REST API, a Celery worker processes them asynchronously, results are stored in PostgreSQL, and clients poll for status or fetch the result.

This is a solo portfolio project. The scan itself is simulated (random height-map data after a short delay); the focus is the asynchronous job lifecycle and the API around it.

## How it works

```
Client --POST /jobs--> FastAPI --writes job (pending)--> PostgreSQL
                          |
                          +--run_scan.delay(job_id)--> Redis (broker)
                                                          |
                                         Celery worker <--+
                                              |
                                  running -> complete / failed
                                              |
                                       result stored in PostgreSQL
Client --GET /jobs/{id}, /jobs/{id}/result--> FastAPI
```

Job states: `pending`, `running`, `complete`, `failed`.

## API

FastAPI generates the OpenAPI 3.0 spec and interactive docs at `/docs`.

| Method | Path | Purpose |
|---|---|---|
| POST | `/jobs` | Submit a scan job (returns `201` with the job id and `pending` status) |
| GET | `/jobs` | List jobs, optionally filtered with `?status=` |
| GET | `/jobs/{id}` | Job status (`404` if unknown) |
| GET | `/jobs/{id}/result` | Scan result (`404` while pending or running, `409` if the job failed) |
| GET | `/health` | Health check |

## Run it

Requires Docker and Docker Compose.

```bash
docker compose up --build
```

The API is then available at http://localhost:8000 (docs at http://localhost:8000/docs).

```bash
curl -X POST http://localhost:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{"parameters": {"scan_size_um": 5.0, "resolution_nm": 1.0}}'
```

## Tests

The tests need a PostgreSQL database named `spm_db_test`. The connection string is read from `TEST_DATABASE_URL`, with a local default of `postgresql+asyncpg://postgres:postgres@localhost:5432/spm_db_test`.

```bash
pip install -r requirements.txt
pytest
```

The API tests run against the real database with the Celery task mocked. The task tests mock the database session and the sleep call.

## CI

GitHub Actions runs on every push and pull request to `master`:

- **Test:** `pytest` against a PostgreSQL 15 service container on Python 3.12.
- **Docker build:** validates the compose file and builds the image.

## Stack

Python 3.12, FastAPI, Celery, Redis, PostgreSQL, SQLAlchemy (async), Pydantic, pytest, Docker Compose.
