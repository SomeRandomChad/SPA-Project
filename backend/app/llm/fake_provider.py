# backend/app/llm/fake_provider.py
from __future__ import annotations

import asyncio
import json
import os
from typing import AsyncIterator


class FakeLLMProvider:
    async def complete(self, prompt: str) -> str:
        # Non-streaming path expects JSON-ish output (your parse_rephrase_response handles extra text)
        payload = {
            "professional": "Please review the attached document.",
            "casual": "Hey, can you take a look at this?",
            "polite": "Could you please review the attached document?",
            "social": "Hey everyone, check this out!",
        }
        return "Sure! Here is the JSON:\n" + json.dumps(payload)

    async def complete_stream(self, prompt: str) -> AsyncIterator[str]:
        """
        Streaming path (per-style) expects PLAIN TEXT for ONE style.
        We detect the requested style from the prompt and stream only that text.
        """
        # Pick the intended style based on the prompt content
        style = "professional"
        p = prompt.lower()
        if " casual " in f" {p} ":
            style = "casual"
        elif " polite " in f" {p} ":
            style = "polite"
        elif " social " in f" {p} " or "social media" in p:
            style = "social"

        outputs = {
            "professional": "Please review the attached document.",
            "casual": "Hey, can you take a look at this?",
            "polite": "Could you please review the attached document?",
            "social": "Hey everyone, check this out!",
        }

        text = outputs[style]

        chunk_size = int(os.getenv("FAKE_STREAM_CHUNK_SIZE", "8"))
        delay_ms = int(os.getenv("FAKE_STREAM_DELAY_MS", "120"))
        delay_s = max(delay_ms, 0) / 1000.0

        for i in range(0, len(text), chunk_size):
            yield text[i : i + chunk_size]
            if delay_s:
                await asyncio.sleep(delay_s)
