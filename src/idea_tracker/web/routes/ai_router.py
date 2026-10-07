from fastapi import APIRouter, Body
from pydantic import BaseModel
from idea_tracker.application.ai_service import AIService

ai_router = APIRouter()
ai_service = AIService()


class StructureRequest(BaseModel):
    raw_text: str


@ai_router.post("/structure-idea")
async def structure_idea(request: StructureRequest):
    """Structure a raw idea into problem statement, risks, assumptions, etc."""
    structured_data = await ai_service.structure_raw_idea(request.raw_text)
    return structured_data


@ai_router.post("/suggest-actions/{idea_id}")
async def suggest_actions(idea_id: int):
    """Suggest 3 concrete next actions for an idea."""
    # TODO: Fetch real idea context from database
    idea_context = {
        "title": "Sample Idea",
        "description": "This is a test idea",
        "status": "INBOX"
    }
    actions = await ai_service.suggest_next_actions(idea_context)
    return {"actions": actions}
