"""Application service for Milestone and Task management."""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from idea_tracker.domain.models.activity import ActivityEvent
from idea_tracker.domain.models.execution import Milestone, Task
from idea_tracker.domain.models.idea import Idea
from idea_tracker.domain.exceptions import EntityNotFoundError


class ExecutionService:
    """Service to handle business logic for execution artifacts."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_idea(self, idea_id: int) -> Idea:
        idea = self.db.get(Idea, idea_id)
        if not idea:
            raise EntityNotFoundError("Idea", idea_id)
        return idea

    def create_milestone(self, idea_id: int, title: str, description: str | None = None) -> Milestone:
        """Create a new milestone for an idea."""
        idea = self.get_idea(idea_id)
        position = self.db.query(Milestone).filter(Milestone.idea_id == idea_id).count()
        milestone = Milestone(idea_id=idea_id, title=title, description=description, position=position)
        self.db.add(milestone)
        self.db.commit()
        self.db.refresh(milestone)
        self._record_event(idea_id, "MILESTONE_CREATED", {"milestone_id": milestone.id, "title": title})
        return milestone

    def complete_milestone(self, milestone_id: int) -> Milestone:
        """Mark a milestone as completed."""
        milestone = self.db.get(Milestone, milestone_id)
        if not milestone:
            raise EntityNotFoundError("Milestone", milestone_id)
        milestone.status = "DONE"
        milestone.completed_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(milestone)
        return milestone

    def create_task(
        self,
        milestone_id: int,
        title: str,
        description: str | None = None,
        priority: str = "MEDIUM",
        due_date: datetime | None = None,
    ) -> Task:
        """Create a new task for a milestone."""
        milestone = self.db.get(Milestone, milestone_id)
        if not milestone:
            raise EntityNotFoundError("Milestone", milestone_id)
        idea = self.get_idea(milestone.idea_id)
        task = Task(milestone_id=milestone_id, title=title, description=description, priority=priority)
        if due_date is not None:
            task.due_date = due_date
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        self._record_event(idea.id, "TASK_CREATED", {"task_id": task.id, "title": title, "priority": priority})
        return task

    def complete_task(self, task_id: int) -> Task:
        """Mark a task as completed."""
        task = self.db.get(Task, task_id)
        if not task:
            raise EntityNotFoundError("Task", task_id)
        task.status = "DONE"
        task.completed_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(task)
        self._record_event(task.milestone.idea_id, "TASK_COMPLETED", {"task_id": task.id})
        return task

    def _record_event(self, idea_id: int, event_type: str, metadata: dict) -> None:
        """Record an activity event for an idea."""
        event = ActivityEvent(
            idea_id=idea_id,
            event_type=event_type,
            event_metadata=__import__("json").dumps(metadata),
            timestamp=datetime.now(timezone.utc),
        )
        self.db.add(event)
        self.db.commit()
