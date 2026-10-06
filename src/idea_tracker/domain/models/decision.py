"""Domain model for Decisions."""

from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship

from idea_tracker.infrastructure.persistence.database import Base


class DecisionOutcome(StrEnum):
    GO = "GO"             # Proceed with the idea
    NO_GO = "NO_GO"       # Kill the idea
    PIVOT = "PIVOT"       # Change direction
    DEFER = "DEFER"       # Put on hold


class Decision(Base):
    __tablename__ = "decisions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    idea_id = Column(Integer, ForeignKey("ideas.id"), nullable=False)
    title = Column(String(200), nullable=False)
    outcome = Column(SQLEnum(DecisionOutcome), nullable=False)
    rationale = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    idea = relationship("Idea", back_populates="decisions")
