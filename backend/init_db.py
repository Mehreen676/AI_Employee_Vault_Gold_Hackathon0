"""
Initialise the database schema.

Usage:
    python -m backend.init_db
"""

from .db import engine, Base
from .models import Task  # noqa: F401 — registers the model with Base


def main() -> None:
    print(f"Connecting to database …")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")


if __name__ == "__main__":
    main()
