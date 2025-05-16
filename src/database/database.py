from os import getenv
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

DATABASE_URL = getenv(
    "DATABASE_URL") or "postgresql://user:password@localhost/database"


engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10
)
