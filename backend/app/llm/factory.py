
from __future__ import annotations

from app.config import get_settings
from app.llm.provider import LLMProvider
from app.llm.fake_provider import FakeLLMProvider
from app.llm.openai_provider import AzureOpenAIProvider

def get_llm_provider() -> LLMProvider:
    settings = get_settings()

    if settings.llm_mode == "fake":
        return FakeLLMProvider()

    if settings.llm_mode == "real":
        if not settings.allow_real_llm:
            raise RuntimeError("LLM_MODE=real set but ALLOW_REAL_LLM is not enabled (set ALLOW_REAL_LLM=1).")
        return AzureOpenAIProvider(settings)

    raise RuntimeError(f"Unsupported LLM_MODE: {settings.llm_mode!r}")   