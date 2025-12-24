# backend/app/llm/parse.py
from __future__ import annotations

import json
from typing import Any

from app.schemas.rephrase import RephraseResponse


class ModelOutputError(Exception):
    """Raised when the LLM output cannot be parsed/validated into the frozen contract."""
    pass


def _strip_code_fences(s: str) -> str:
    s = s.strip()
    if s.startswith("```"):
        # Handles ```json ... ``` or ``` ... ```
        lines = s.splitlines()
        if len(lines) >= 2 and lines[0].startswith("```"):
            # drop first fence line
            lines = lines[1:]
        # drop last fence line if present
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        return "\n".join(lines).strip()
    return s


def _extract_json_object(s: str) -> str:
    """
    Best-effort extraction:
    - If the model returns extra text, pull out the first {...} block.
    """
    s = s.strip()
    start = s.find("{")
    end = s.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ModelOutputError("No JSON object found in model output.")
    return s[start : end + 1]


def parse_rephrase_response(model_text: str) -> RephraseResponse:
    """
    Convert raw model output -> validated RephraseResponse.
    Raises ModelOutputError on parse/validation problems.
    """
    if not isinstance(model_text, str) or not model_text.strip():
        raise ModelOutputError("Empty model output.")

    cleaned = _strip_code_fences(model_text)
    json_str = _extract_json_object(cleaned)

    try:
        data: Any = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ModelOutputError(f"Invalid JSON: {e.msg}") from e

    # Validate against frozen contract
    try:
        return RephraseResponse.model_validate(data)
    except Exception as e:
        raise ModelOutputError("JSON did not match the frozen response contract.") from e
