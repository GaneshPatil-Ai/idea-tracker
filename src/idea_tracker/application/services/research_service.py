"""Service for managing research evidence and questions."""

from datetime import datetime, UTC

from sqlalchemy.orm import Session

from idea_tracker.domain.exceptions import EntityNotFoundError
from idea_tracker.domain.models.activity import ActivityEvent
from idea_tracker.domain.models.idea import Idea
from idea_tracker.domain.models.research import EvidenceType, ResearchEvidence, ResearchQuestion


class ResearchService:
    """Service to handle business logic for research evidence and questions."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def add_evidence(
        self,
        idea_id: int,
        title: str,
        url: str,
        evidence_type: EvidenceType,
        author: str | None = None,
        publication_date: datetime | None = None,
        summary: str | None = None,
    ) -> ResearchEvidence:
        """Add research evidence to an idea."""
        self.get_idea(idea_id)  # Validate idea exists
        evidence = ResearchEvidence(
            idea_id=idea_id,
            title=title,
            url=url,
            evidence_type=evidence_type,
            author=author,
            publication_date=publication_date,
            summary=summary,
        )
        self.db.add(evidence)
        self.db.commit()
        self.db.refresh(evidence)

        self._record_event(
            idea_id,
            "EVIDENCE_ADDED",
            {
                "evidence_id": evidence.id,
                "title": title,
                "type": evidence_type.value,
            },
        )
        return evidence

    def get_evidence_for_idea(self, idea_id: int) -> list[ResearchEvidence]:
        """Retrieve all research evidence for an idea."""
        self.get_idea(idea_id)  # Validate idea exists
        return (
            self.db.query(ResearchEvidence)
            .filter(ResearchEvidence.idea_id == idea_id)
            .order_by(ResearchEvidence.created_at.desc())
            .all()
        )

    def add_research_question(
        self,
        idea_id: int,
        question: str,
    ) -> ResearchQuestion:
        """Add a research question to an idea."""
        self.get_idea(idea_id)  # Validate idea exists
        research_question = ResearchQuestion(
            idea_id=idea_id,
            question=question,
            status="PENDING",
        )
        self.db.add(research_question)
        self.db.commit()
        self.db.refresh(research_question)

        self._record_event(
            idea_id,
            "RESEARCH_QUESTION_ADDED",
            {
                "question_id": research_question.id,
                "question": question,
            },
        )
        return research_question

    def mark_question_answered(self, question_id: int) -> ResearchQuestion:
        """Mark a research question as answered."""
        question = self.db.get(ResearchQuestion, question_id)
        if not question:
            raise EntityNotFoundError("ResearchQuestion", question_id)
        question.status = "ANSWERED"
        self.db.commit()
        self.db.refresh(question)

        self._record_event(
            question.idea_id,
            "RESEARCH_QUESTION_ANSWERED",
            {"question_id": question.id},
        )
        return question

    def get_questions_for_idea(self, idea_id: int) -> list[ResearchQuestion]:
        """Retrieve all research questions for an idea."""
        self.get_idea(idea_id)  # Validate idea exists
        return (
            self.db.query(ResearchQuestion)
            .filter(ResearchQuestion.idea_id == idea_id)
            .order_by(ResearchQuestion.created_at.desc())
            .all()
        )

    def get_idea(self, idea_id: int) -> Idea:
        """Retrieve an idea by ID, raising if not found."""
        idea = self.db.get(Idea, idea_id)
        if not idea:
            raise EntityNotFoundError("Idea", idea_id)
        return idea

    def _record_event(self, idea_id: int, event_type: str, metadata: dict) -> None:
        """Record an activity event for an idea."""
        event = ActivityEvent(
            idea_id=idea_id,
            event_type=event_type,
            event_metadata=__import__("json").dumps(metadata),
            timestamp=datetime.now(UTC),
        )
        self.db.add(event)
        self.db.commit()
