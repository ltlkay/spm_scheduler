from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import create_tables
from app.routers import jobs

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield

app = FastAPI(title="SPM Job Scheduler", lifespan=lifespan)
app.include_router(jobs.router)

@app.get("/health")
async def health():
    return {"status": "ok"}
