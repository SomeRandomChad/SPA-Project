# backend/app/llm/prompt.py
from __future__ import annotations


def build_rephrase_prompt(text: str) -> str:
    """
    Build a single prompt that asks for STRICT JSON output with the frozen keys.
    Keep this as a pure function for easy testing.
    """
    return f"""You are a writing assistant.

Rephrase the input text into exactly four styles:
- professional
- casual
- polite
- social

Return ONLY valid JSON with exactly these keys:
professional, casual, polite, social

No markdown. No code fences. No extra keys. No explanations.

Input text:
{text}
"""
