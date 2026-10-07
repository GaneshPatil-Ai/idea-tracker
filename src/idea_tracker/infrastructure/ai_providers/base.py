from abc import ABC, abstractmethod
from typing import List, Dict, Any

class AIProvider(ABC):
    @abstractmethod
    async def structure_idea(self, raw_text: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def suggest_next_actions(self, idea_context: Dict[str, Any]) -> List[str]:
        pass
