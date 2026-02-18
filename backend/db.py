"""
Database engine and session factory.

Reads DATABASE_URL from the environment (Neon Postgres).
If DATABASE_URL is not set, engine/SessionLocal are None — the app
still runs but without DB persistence (graceful degradation).

Exports: DATABASE_URL, engine, SessionLocal, Base, db_available.
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "")

Base = declarative_base()

if DATABASE_URL:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db_available = True
else:
    engine = None
    SessionLocal = None
    db_available = False
