# backend/app/llm/provider_errors.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class LLMProviderError(Exception):
    """Normalized upstream/provider failure that will be mapped to an API Error response."""
    status_code: int
    code: str
    message: str
    retry_after_seconds: Optional[int] = None
