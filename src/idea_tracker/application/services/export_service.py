"""Export service for data portability."""

import json
from datetime import datetime, UTC
from pathlib import Path

from sqlalchemy.orm import Session

from idea_tracker.domain.models.idea import Idea
from idea_tracker.domain.models.activity import ActivityEvent
from idea_tracker.domain.models.content import Note, Tag
from idea_tracker.domain.models.decision import Decision
from idea_tracker.domain.models.execution import Milestone, Task
from idea_tracker.domain.models.research import ResearchEvidence, ResearchQuestion


class ExportService:
    """Service for exporting ideas to JSON and markdown formats."""

    def __init__(self, db: Session):
        self.db = db

    def export_all_ideas(self, format: str = "json") -> str:
        """Export all ideas in specified format.

        Args:
            format: 'json' or 'markdown'

        Returns:
            Serialized data as string
        """
        ideas = self.db.query(Idea).all()

        if format == "json":
            return self._export_to_json(ideas)
        elif format == "markdown":
            return self._export_to_markdown(ideas)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def export_idea(self, idea_id: int, format: str = "json") -> str:
        """Export single idea with all related content.

        Args:
            idea_id: Idea to export
            format: 'json' or 'markdown'

        Returns:
            Serialized data as string
        """
        idea = self.db.get(Idea, idea_id)
        if not idea:
            raise ValueError(f"Idea {idea_id} not found")

        if format == "json":
            return self._idea_to_json(idea)
        elif format == "markdown":
            return self._idea_to_markdown(idea)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _export_to_json(self, ideas: list[Idea]) -> str:
        """Export ideas as JSON."""
        data = {
            "export_date": datetime.now(UTC).isoformat(),
            "total_ideas": len(ideas),
            "ideas": [self._serialize_idea(idea) for idea in ideas],
        }
        return json.dumps(data, indent=2, default=str)

    def _export_to_markdown(self, ideas: list[Idea]) -> str:
        """Export ideas as markdown."""
        lines = [
            "# Idea Tracker Export",
            f"Exported: {datetime.now(UTC).isoformat()}",
            f"Total Ideas: {len(ideas)}",
            "",
        ]

        for idea in ideas:
            lines.append(self._idea_to_markdown(idea))
            lines.append("")

        return "\n".join(lines)

    def _serialize_idea(self, idea: Idea) -> dict:
        """Serialize idea to dictionary."""
        return {
            "id": idea.id,
            "title": idea.title,
            "status": idea.status.value,
            "raw_description": idea.raw_description,
            "structured_description": idea.structured_description,
            "source": idea.source.value,
            "created_at": idea.created_at.isoformat(),
            "updated_at": idea.updated_at.isoformat(),
            "last_reviewed_at": idea.last_reviewed_at.isoformat() if idea.last_reviewed_at else None,
            "tags": [tag.name for tag in idea.tags],
            "notes": [{"content": note.content, "created_at": note.created_at.isoformat()} for note in idea.notes],
            "decisions": [
                {
                    "title": d.title,
                    "outcome": d.outcome.value,
                    "rationale": d.rationale,
                    "created_at": d.created_at.isoformat(),
                }
                for d in idea.decisions
            ],
            "milestones": [
                {
                    "title": m.title,
                    "status": m.status,
                    "tasks": [
                        {
                            "title": t.title,
                            "status": t.status,
                            "priority": t.priority,
                        }
                        for t in m.tasks
                    ],
                }
                for m in idea.milestones
            ] if hasattr(idea, 'milestones') else [],
            "research_evidence": [
                {
                    "title": e.title,
                    "url": e.url,
                    "type": e.evidence_type.value,
                    "author": e.author,
                }
                for e in idea.research_evidence
            ] if hasattr(idea, 'research_evidence') else [],
            "research_questions": [
                {
                    "question": q.question,
                    "status": q.status,
                }
                for q in idea.research_questions
            ] if hasattr(idea, 'research_questions') else [],
        }

    def _idea_to_json(self, idea: Idea) -> str:
        """Export single idea to JSON."""
        data = {"idea": self._serialize_idea(idea)}
        return json.dumps(data, indent=2, default=str)

    def _idea_to_markdown(self, idea: Idea) -> str:
        """Export single idea to markdown."""
        lines = [
            f"## {idea.title}",
            f"**Status**: {idea.status.value}",
            f"**Created**: {idea.created_at.isoformat()}",
            "",
            "### Description",
            idea.raw_description,
            "",
        ]

        if idea.structured_description:
            lines.extend([
                "### Structured Description",
                idea.structured_description,
                "",
            ])

        if idea.tags:
            lines.append(f"**Tags**: {', '.join([tag.name for tag in idea.tags])}")
            lines.append("")

        if idea.notes:
            lines.append("### Notes")
            for note in idea.notes:
                lines.append(f"- {note.content}")
            lines.append("")

        if idea.decisions:
            lines.append("### Decisions")
            for decision in idea.decisions:
                lines.append(f"- **{decision.title}**: {decision.outcome.value}")
                lines.append(f"  - Rationale: {decision.rationale}")
            lines.append("")

        return "\n".join(lines)
