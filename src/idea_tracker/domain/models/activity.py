"""Domain model for ActivityEvent."""

from datetime import datetime, UTC

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from idea_tracker.infrastructure.persistence.database import Base


class ActivityEvent(Base):
    __tablename__ = "activity_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    idea_id = Column(Integer, ForeignKey("ideas.id"), nullable=False)
    event_type = Column(String(50), nullable=False)
    actor = Column(String(50), default="system")
    timestamp = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    # Stored as serialized JSON string
    event_metadata = Column("metadata", String(2000), nullable=True)

    idea = relationship("Idea", back_populates="events")

