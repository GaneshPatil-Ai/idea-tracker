"""Domain exceptions for Idea Tracker.

Zero external dependencies — pure Python domain exceptions.
"""


class IdeaTrackerError(Exception):
    """Base exception for all idea tracker domain errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class EntityNotFoundError(IdeaTrackerError):
    """Raised when an entity (Idea, Task, Note, etc.) is not found."""

    def __init__(self, entity_type: str, entity_id: str | int) -> None:
        self.entity_type = entity_type
        self.entity_id = entity_id
        super().__init__(f"{entity_type} with ID '{entity_id}' not found.")


class InvalidTransitionError(IdeaTrackerError):
    """Raised when an invalid lifecycle transition is attempted."""

    def __init__(self, current_state: str, target_state: str, reason: str = "") -> None:
        self.current_state = current_state
        self.target_state = target_state
        msg = f"Cannot transition from {current_state} to {target_state}."
        if reason:
            msg += f" Reason: {reason}"
        super().__init__(msg)


class ValidationError(IdeaTrackerError):
    """Raised when domain validation fails."""

    pass


class AIServiceError(IdeaTrackerError):
    """Raised when AI service fails to process input or returns malformed response."""

    def __init__(self, message: str, raw_response: str | None = None) -> None:
        self.raw_response = raw_response
        super().__init__(message)


class ConfigurationError(IdeaTrackerError):
    """Raised when application or service configuration is missing or invalid."""

    pass
