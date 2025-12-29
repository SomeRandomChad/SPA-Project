# backend/app/routes/rephrase.py
from __future__ import annotations

import asyncio
import json
from typing import AsyncGenerator, Dict, Iterable

from fastapi import APIRouter, HTTPException, Request
from starlette.responses import StreamingResponse

from app.schemas.rephrase import RephraseRequest, RephraseResponse
from app.services.rephrase import rephrase_service, ValidationError
from app.llm.factory import get_llm_provider
from app.llm.rephrase_generator import generate_rephrases, generate_rephrases_stream
from app.llm.provider_errors import LLMProviderError
from app.llm.parse import ModelOutputError

router = APIRouter()


@router.post("/rephrase", response_model=RephraseResponse)
async def rephrase_endpoint(req: RephraseRequest):
    try:
        return await rephrase_service(req)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


def _sse(event: str, data: Dict) -> bytes:
    payload = json.dumps(data, ensure_ascii=False)
    return f"event: {event}\n" f"data: {payload}\n\n".encode("utf-8")


def _chunks(s: str, size: int) -> Iterable[str]:
    for i in range(0, len(s), size):
        yield s[i : i + size]


@router.post("/rephrase/stream")
async def rephrase_stream_endpoint(req: RephraseRequest, request: Request):
    async def event_stream() -> AsyncGenerator[bytes, None]:
        yield b": stream-open\n\n"
        if await request.is_disconnected():
            return

        text = req.text.strip()
        if not text:
            yield _sse(
                "error",
                {"code": "VALIDATION_ERROR", "message": "Invalid request: text (min_length)", "details": []},
            )
            return

        try:
            provider = get_llm_provider()

            if await request.is_disconnected():
                return

            # Assemble per-style outputs 
            assembled: Dict[str, str] = {
                "professional": "",
                "casual": "",
                "polite": "",
                "social": "",
            }

            async for item in generate_rephrases_stream(provider, text):
                if await request.is_disconnected():
                    return
                style = item["style"]
                delta = item["delta"]
                assembled[style] += delta
                yield _sse("partial", {"style": style, "delta": delta})

            final = RephraseResponse(
                professional=assembled["professional"].strip(),
                casual=assembled["casual"].strip(),
                polite=assembled["polite"].strip(),
                social=assembled["social"].strip(),
            )

        except LLMProviderError as e:
            yield _sse("error", {"code": e.code, "message": e.message, "details": []})
            return
        except ModelOutputError:
            yield _sse("error", {"code": "INTERNAL_ERROR", "message": "Invalid model output.", "details": []})
            return
        except Exception:
            yield _sse("error", {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred.", "details": []})
            return

        if await request.is_disconnected():
            return

        yield _sse(
            "final",
            {
                "professional": final.professional,
                "casual": final.casual,
                "polite": final.polite,
                "social": final.social,
            },
        )

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )