# backend/app/llm/rephrase_generator.py
from __future__ import annotations

from typing import AsyncGenerator, Dict, Literal

from app.llm.parse import parse_rephrase_response
from app.llm.prompt import build_rephrase_prompt
from app.llm.provider import LLMProvider
from app.schemas.rephrase import RephraseResponse


async def generate_rephrases(provider: LLMProvider, text: str) -> RephraseResponse:
    prompt = build_rephrase_prompt(text)
    raw = await provider.complete(prompt)
    return parse_rephrase_response(raw)

Style = Literal["professional", "casual", "polite", "social"]


def _build_single_style_prompt(text: str, style: Style) -> str:
    # Keep it boring and explicit: return ONLY plain text, no JSON, no markdown.
    # This makes token streaming trivial to map into one panel.
    return (
        f"You are a writing assistant.\n"
        f"Rewrite the INPUT in a {style} style.\n"
        f"Rules:\n"
        f"- Return ONLY the rewritten text.\n"
        f"- Do NOT include quotes, code fences, JSON, or extra commentary.\n"
        f"- Preserve meaning.\n\n"
        f"INPUT:\n{text}\n"
    )


async def generate_rephrases_stream(
    provider: LLMProvider, text: str
) -> AsyncGenerator[Dict[str, str], None]:
    """
    Streams per-style deltas:
      yields {"style": "<style>", "delta": "<text_delta>"}
    At the end, yields {"final": "<json_string>"} is NOT done here (route will assemble final).
    """
    styles: list[Style] = ["professional", "casual", "polite", "social"]
    for style in styles:
        prompt = _build_single_style_prompt(text, style)
        async for delta in provider.complete_stream(prompt):
            yield {"style": style, "delta": delta}