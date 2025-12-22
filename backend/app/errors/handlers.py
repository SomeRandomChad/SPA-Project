# backend/app/errors/handlers.py
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


def _field_from_loc(loc: Tuple[Any, ...]) -> str:
    """
      ("body", "text")
      ("query", "limit")
      ("body", "items", 0, "name")
    """
    parts = [str(p) for p in loc if p is not None]
    if parts and parts[0] in ("body", "query", "path", "header", "cookie"):
        parts = parts[1:]
    return ".".join(parts) if parts else "request"


def _issue_from_pydantic_type(err_type: str) -> str:
    mapping = {
        "missing": "required",
        "string_too_short": "min_length",
        "string_too_long": "max_length",
        "string_type": "type",
        "type_error.str": "type",
        "value_error.jsondecode": "malformed_json",
    }
    return mapping.get(err_type, err_type)


async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()

    details: List[Dict[str, str]] = []
    for e in errors:
        loc = tuple(e.get("loc", ()))
        err_type = str(e.get("type", "validation_error"))
        msg = str(e.get("msg", "Invalid request"))

        field = _field_from_loc(loc)
        issue = _issue_from_pydantic_type(err_type)

        item: Dict[str, str] = {"field": field, "issue": issue}

        # Optional hint. Keep it short; this is user-facing.
        # You can also derive hints from ctx (min_length/max_length) if you want.
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

    # Build a stable, readable top-level message.
    # Prefer the first error for the summary.
    if details:
        first = details[0]
        field = first.get("field", "request")
        issue = first.get("issue", "validation_error")
        message = f"Invalid request: {field} ({issue})"
    else:
        message = "Invalid request."

    payload = {
        "code": "VALIDATION_ERROR",
        "message": message,
        "details": details,
    }

    return JSONResponse(status_code=400, content=payload)
