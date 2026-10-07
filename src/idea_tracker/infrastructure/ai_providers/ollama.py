import httpx
import json
import os
import re
from typing import Any

from .base import AIProvider


STRUCTURE_PROMPT = """You are an idea analyst. Given a raw idea, extract and return ONLY a valid JSON object with these fields:
{
  "problem_statement": "clear 1-2 sentence problem this solves",
  "target_users": ["user type 1", "user type 2"],
  "opportunities": ["opportunity 1", "opportunity 2"],
  "risks": ["risk 1", "risk 2"],
  "assumptions": ["assumption 1", "assumption 2"]
}

Raw Idea: {raw_text}

Return ONLY the JSON object, no explanation."""

NEXT_ACTIONS_PROMPT = """You are an execution coach. Given this idea context, suggest exactly 3 concrete, specific next actions.
Return ONLY a valid JSON array of strings, no explanation.

Idea: {title}
Description: {description}
Status: {status}

Example format: ["Action 1", "Action 2", "Action 3"]"""


class OllamaProvider(AIProvider):
    """OpenAI-compatible provider — works with Ollama, Omniroute, or any OpenAI-compatible endpoint."""

    def __init__(self, base_url: str, model: str):
        api_key = os.getenv("OPENAI_API_KEY", "")
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        self.client = httpx.AsyncClient(base_url=base_url, headers=headers, timeout=30.0)
        self.model = model

    async def _chat(self, prompt: str) -> str:
        """Call OpenAI-compatible /chat/completions endpoint."""
        response = await self.client.post(
            "/chat/completions",
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
            },
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    async def structure_idea(self, raw_text: str) -> dict:
        """Structure a raw idea into problem statement, risks, opportunities, etc."""
        content = await self._chat(STRUCTURE_PROMPT.format(raw_text=raw_text))
        return self._extract_json(content, default={
            "problem_statement": raw_text[:200],
            "target_users": [],
            "opportunities": [],
            "risks": [],
            "assumptions": [],
        })

    async def suggest_next_actions(self, idea_context: dict) -> list[str]:
        """Suggest 3 concrete next actions for the given idea."""
        content = await self._chat(NEXT_ACTIONS_PROMPT.format(
            title=idea_context.get("title", ""),
            description=idea_context.get("description", ""),
            status=idea_context.get("status", "INBOX"),
        ))
        result = self._extract_json(content, default=[
            "Define the problem clearly with 1 user interview",
            "Sketch a minimal prototype in 1 hour",
            "Identify 3 competing solutions and their weaknesses",
        ])
        return result if isinstance(result, list) else list(result.values())

    def _extract_json(self, text: str, default: Any) -> Any:
        """Extract JSON from LLM response, handling markdown code blocks."""
        # Strip markdown code fences if present
        text = re.sub(r"```(?:json)?\s*", "", text).strip().rstrip("`").strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Try extracting first JSON object or array
            match = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError:
                    pass
        return default
