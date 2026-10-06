"""Domain models for ResearchEvidence and ResearchQuestion."""

from datetime import datetime, UTC
from enum import StrEnum
from typing import Optional

from sqlalchemy import Column, DateTime, Enum as SQLEnum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from idea_tracker.infrastructure.persistence.database import Base


class EvidenceType(StrEnum):
    ARTICLE = "ARTICLE"
    VIDEO = "VIDEO"
    PODCAST = "PODCAST"
    DOCUMENT = "DOCUMENT"
    INTERVIEW = "INTERVIEW"
    WEBSITE = "WEBSITE"
    STUDY = "STUDY"
    OTHER = "OTHER"


class ResearchEvidence(Base):
    __tablename__ = "research_evidence"

    id = Column(Integer, primary_key=True, autoincrement=True)
    idea_id = Column(Integer, ForeignKey("ideas.id"), nullable=False)
    title = Column(String(200), nullable=False)
    url = Column(String(500), nullable=False)
    evidence_type = Column(SQLEnum(EvidenceType), nullable=False)
    author = Column(String(200), nullable=True)
    publication_date = Column(DateTime, nullable=True)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    idea = relationship("Idea", back_populates="research_evidence")


class ResearchQuestion(Base):
    __tablename__ = "research_questions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    idea_id = Column(Integer, ForeignKey("ideas.id"), nullable=False)
    question = Column(Text, nullable=False)
    status = Column(String(50), default="PENDING", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    idea = relationship("Idea", back_populates="research_questions")
