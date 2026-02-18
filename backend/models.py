"""
SQLAlchemy ORM models for the Gold Tier vault.

Tables:
  - tasks      : vault task records
  - agent_runs : one row per Gold Agent execution
  - events     : audit trail events (FK -> agent_runs)
"""

from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime
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


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(Integer, primary_key=True, index=True)
    run_ts = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    model = Column(String(100), nullable=False, default="")
    loops = Column(Integer, nullable=False, default=0)
    processed = Column(Integer, nullable=False, default=0)
    failed = Column(Integer, nullable=False, default=0)

    def __repr__(self) -> str:
        return f"<AgentRun id={self.id} processed={self.processed} failed={self.failed}>"


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("agent_runs.id"), nullable=True, index=True)
    ts = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    event_type = Column(String(200), nullable=False, default="")
    payload_json = Column(Text, nullable=False, default="{}")

    def __repr__(self) -> str:
        return f"<Event id={self.id} run_id={self.run_id} type={self.event_type!r}>"
