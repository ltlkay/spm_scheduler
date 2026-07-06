import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.base import Base

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:secret!@localhost:5432/spm_db")

engine = create_async_engine(DATABASE_URL, echo=False)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)



async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def create_tables():
    async with engine.begin() as conn:
        from app import models
        await conn.run_sync(Base.metadata.create_all)
