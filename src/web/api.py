from fastapi import APIRouter
from src.application.ai_service import AIService

ai_router = APIRouter()
ai_service = AIService()

@ai_router.post("/structure-idea")
async def structure_idea(raw_text: str):
    structured_data = await ai_service.structure_raw_idea(raw_text)
    return structured_data

@ai_router.post("/suggest-actions/{idea_id}")
async def suggest_actions(idea_id: int):
    # In a real implementation, fetch idea context from domain layer
    idea_context = {
        "title": "Sample Idea",  # Replace with actual idea data
        "description": "This is a test idea",
        "state": "INBOX"
    }
    actions = await ai_service.suggest_next_actions(idea_context)
    return {"actions": actions}
