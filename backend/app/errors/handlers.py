# backend/app/errors/handlers.py
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.llm.provider_errors import LLMProviderError
# Optional: if you want explicit typing here, uncomment:
# from app.llm.parse import ModelOutputError


def _field_from_loc(loc: Tuple[Any, ...]) -> str:
    """
    FastAPI/Pydantic loc examples:
      ("body", "text")
      ("query", "limit")
      ("body", "items", 0, "name")
    """
    parts = [str(p) for p in loc if p is not None]
    if parts and parts[0] in ("body", "query", "path", "header", "cookie"):
        parts = parts[1:]
    return ".".join(parts) if parts else "request"


def _issue_from_pydantic_type(err_type: str) -> str:
    """
    Map Pydantic error types to stable-ish issue codes.
    """
    mapping = {
        "missing": "required",
        "string_too_short": "min_length",
        "string_too_long": "max_length",
        "string_type": "type",
        "type_error.str": "type",
        "value_error.jsondecode": "malformed_json",
    }
    return mapping.get(err_type, err_type)


async def request_validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Normalize FastAPI/Pydantic request validation errors into HTTP 400.
    """
    errors = exc.errors()

    details: List[Dict[str, str]] = []
    for e in errors:
        loc = tuple(e.get("loc", ()))
        err_type = str(e.get("type", "validation_error"))

        field = _field_from_loc(loc)
        issue = _issue_from_pydantic_type(err_type)

        item: Dict[str, str] = {"field": field, "issue": issue}

        ctx = e.get("ctx") or {}
        hint: Optional[str] = None
        if issue == "required":
            hint = "This field is required."
        elif issue == "min_length" and "min_length" in ctx:
            hint = f"Must be at least {ctx['min_length']} character(s)."
        elif issue == "max_length" and "max_length" in ctx:
            hint = f"Must be at most {ctx['max_length']} character(s)."
        elif issue == "type":
            hint = "Wrong type for this field."
        elif issue == "malformed_json":
            hint = "Request body must be valid JSON."

        if hint:
            item["hint"] = hint

        details.append(item)

    if details:
        first = details[0]
        message = f"Invalid request: {first.get('field', 'request')} ({first.get('issue', 'validation_error')})"
    else:
        message = "Invalid request."

    return JSONResponse(
        status_code=400,
        content={"code": "VALIDATION_ERROR", "message": message, "details": details},
    )


async def llm_provider_exception_handler(request: Request, exc: LLMProviderError) -> JSONResponse:
    headers: Dict[str, str] = {}
    if exc.status_code == 429 and exc.retry_after_seconds is not None:
        headers["Retry-After"] = str(exc.retry_after_seconds)

    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.code, "message": exc.message, "details": []},
        headers=headers,
    )


async def model_output_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    # If you prefer explicit typing, change `exc: Exception` to `exc: ModelOutputError`
    return JSONResponse(
        status_code=500,
        content={"code": "INTERNAL_ERROR", "message": "Invalid model output.", "details": []},
    )
