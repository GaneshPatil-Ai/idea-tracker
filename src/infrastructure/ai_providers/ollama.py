import httpx
import json
from .base import AIProvider

class OllamaProvider(AIProvider):
    def __init__(self, base_url: str, model: str):
        self.client = httpx.AsyncClient(base_url=base_url)
        self.model = model

    async def structure_idea(self, raw_text: str) -> dict:
        response = await self.client.post(
            "/generate",
            json={
                "model": self.model,
                "prompt": f"""\n                Structure this raw idea into JSON with fields:\n                - problem_statement\n                - target_users\n                - opportunities\n                - risks\n                - assumptions\n                \n                Raw Idea: {raw_text}\n                """
            }
        )
        response.raise_for_status()
        return self._parse_response(response.json())

    async def suggest_next_actions(self, idea_context: dict) -> list[str]:
        response = await self.client.post(
            "/generate",
            json={
                "model": self.model,
                "prompt": f"""\n                Suggest 3 concrete next actions for this idea based on its context.\n                Return as a JSON array of strings.\n                \n                Idea Context:\n                {json.dumps(idea_context, indent=2)}\n                """
            }
        )
        response.raise_for_status()
        return self._parse_response(response.json())

    def _parse_response(self, response: dict) -> Any:
        # Extract JSON from LLM output
        raw_output = response.get("response", "{}")
        try:
            return json.loads(raw_output)
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON from LLM: {raw_output[:100]}...")
