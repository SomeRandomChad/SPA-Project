# backend/app/llm/fake_provider.py
from __future__ import annotations

import json


class FakeLLMProvider:
    async def complete(self, prompt: str) -> str:
        # Simulate a realistic LLM response: sometimes extra text around JSON.
        payload = {
            "professional": "Please review the attached document.",
            "casual": "Hey, can you take a look at this?",
            "polite": "Could you please review the attached document?",
            "social": "Hey everyone, check this out!",
        }

        return "Sure! Here is the JSON:\n" + json.dumps(payload)