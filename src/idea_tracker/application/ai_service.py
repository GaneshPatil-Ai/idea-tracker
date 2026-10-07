from idea_tracker.infrastructure.ai_providers import get_ai_provider

class AIService:
    def __init__(self):
        self.provider = get_ai_provider()

    async def structure_raw_idea(self, raw_text: str) -> dict:
        return await self.provider.structure_idea(raw_text)

    async def suggest_next_actions(self, idea_context: dict) -> list[str]:
        return await self.provider.suggest_next_actions(idea_context)
