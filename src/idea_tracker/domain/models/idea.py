"""Domain model for Idea."""

from datetime import datetime, timezone
from enum import StrEnum
from typing import Optional

from sqlalchemy import Column, DateTime, Enum as SQLEnum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from idea_tracker.infrastructure.persistence.database import Base


class StatusEnum(StrEnum):
    INBOX = "INBOX"
    STRUCTURED = "STRUCTURED"
    EXPLORING = "EXPLORING"
    VALIDATING = "VALIDATING"
    COMMITTED = "COMMITTED"
    BUILDING = "BUILDING"
    LAUNCHED = "LAUNCHED"
    PAUSED = "PAUSED"
    KILLED = "KILLED"
    ABANDONED = "ABANDONED"


class SourceEnum(StrEnum):
    MANUAL = "MANUAL"
    QUICK_CAPTURE = "QUICK_CAPTURE"
    IMPORT = "IMPORT"
    API = "API"


class Idea(Base):
    __tablename__ = "ideas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    raw_description = Column(String(1000), nullable=False)
    structured_description = Column(String(2000), nullable=True)
    status = Column(SQLEnum(StatusEnum), default=StatusEnum.INBOX, nullable=False)
    source = Column(SQLEnum(SourceEnum), default=SourceEnum.MANUAL, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    last_reviewed_at = Column(DateTime, nullable=True)

    tags = relationship("Tag", secondary="idea_tags", back_populates="ideas")
    notes = relationship("Note", back_populates="idea", cascade="all, delete-orphan")
    events = relationship("ActivityEvent", back_populates="idea", cascade="all, delete-orphan")
