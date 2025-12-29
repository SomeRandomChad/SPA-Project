from __future__ import annotations

from app.config import get_settings
from app.llm.provider import LLMProvider
from app.llm.fake_provider import FakeLLMProvider
from app.llm.openai_provider import AzureOpenAIProvider
from app.llm.provider_errors import LLMProviderError 


def get_llm_provider() -> LLMProvider:
    settings = get_settings()

    if settings.llm_mode == "fake":
        return FakeLLMProvider()

    if settings.llm_mode == "real":
        if not settings.allow_real_llm:
            raise LLMProviderError(
                status_code=403,
                code="REAL_LLM_DISABLED",
                message="Real LLM calls are disabled. Set ALLOW_REAL_LLM=1 to enable.",
            )
        return AzureOpenAIProvider(settings)

    raise RuntimeError(f"Unsupported LLM_MODE: {settings.llm_mode!r}")