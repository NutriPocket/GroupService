from os import getenv
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

DATABASE_URL = getenv(
    "DATABASE_URL", "postgresql://user:password@0.0.0.0:5433/database")

print(f"Connecting to database at {DATABASE_URL}")

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10
)
