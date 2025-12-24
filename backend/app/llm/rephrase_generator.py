# backend/app/llm/rephrase_generator.py
from __future__ import annotations

from app.llm.parse import parse_rephrase_response
from app.llm.prompt import build_rephrase_prompt
from app.llm.provider import LLMProvider
from app.schemas.rephrase import RephraseResponse


async def generate_rephrases(provider: LLMProvider, text: str) -> RephraseResponse:
    prompt = build_rephrase_prompt(text)
    raw = await provider.complete(prompt)
    return parse_rephrase_response(raw)
