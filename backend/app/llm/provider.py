# backend/app/llm/provider.py
from __future__ import annotations

from typing import AsyncIterator, Protocol


class LLMProvider(Protocol):
    async def complete(self, prompt: str) -> str:
        """Non-streaming completion."""
        ...

    async def complete_stream(self, prompt: str) -> AsyncIterator[str]:
        """Stream text deltas as they are produced by the provider. Yield ONLY text."""
        ...