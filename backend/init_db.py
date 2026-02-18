"""
Initialise the database schema.

Usage:
    python -m backend.init_db
"""

from .db import engine, db_available, Base
# Import models so they register with Base.metadata
from .models import Task, AgentRun, Event  # noqa: F401


def main() -> None:
    if not db_available:
        print("DATABASE_URL not set — skipping DB init.")
        return

    print("Connecting to database ...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")


if __name__ == "__main__":
    main()
