"""Domain models for Milestone and Task."""

from datetime import date, datetime, timezone
from enum import StrEnum
from typing import Optional

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from idea_tracker.infrastructure.persistence.database import Base


class TaskStatus(StrEnum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"
    BLOCKED = "BLOCKED"
    CANCELLED = "CANCELLED"


class TaskPriority(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Milestone(Base):
    __tablename__ = "milestones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    idea_id = Column(Integer, ForeignKey("ideas.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(String(1000), nullable=True)
    status = Column(String(50), default="TODO", nullable=False)
    position = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at = Column(DateTime, nullable=True)

    tasks = relationship("Task", back_populates="milestone", cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    milestone_id = Column(Integer, ForeignKey("milestones.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(String(1000), nullable=True)
    status = Column(String(50), default="TODO", nullable=False)
    priority = Column(String(50), default="MEDIUM", nullable=False)
    due_date = Column(Date, nullable=True)
    effort = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at = Column(DateTime, nullable=True)

    milestone = relationship("Milestone", back_populates="tasks")
