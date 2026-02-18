"""
SQLAlchemy ORM models for the Gold Tier vault.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func

from .db import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), unique=True, index=True, nullable=False)
    title = Column(String(500), nullable=False, default="")
    description = Column(Text, nullable=False, default="")
    status = Column(String(50), nullable=False, default="pending", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Task id={self.id} filename={self.filename!r} status={self.status!r}>"
