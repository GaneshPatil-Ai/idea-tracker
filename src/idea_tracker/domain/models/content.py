"""Domain models for Tags and Notes."""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from idea_tracker.infrastructure.persistence.database import Base

idea_tags = Table(
    "idea_tags",
    Base.metadata,
    Column("idea_id", ForeignKey("ideas.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)

    ideas = relationship("Idea", secondary=idea_tags, back_populates="tags")


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    idea_id = Column(Integer, ForeignKey("ideas.id"), nullable=False)
    content = Column(String(2000), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    idea = relationship("Idea", back_populates="notes")
