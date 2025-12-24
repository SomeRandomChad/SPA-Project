# backend/app/llm/provider.py
from __future__ import annotations

from typing import Protocol


class LLMProvider(Protocol):
    async def complete(self, prompt: str) -> str:
        """Return raw text output from the model (not parsed)."""
        ...
