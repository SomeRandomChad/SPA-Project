from __future__ import annotations

import os
from dataclasses import dataclass

def _truthy(s: str | None) -> bool:
    return (s or "").strip().lower() in ("1", "true", "yes", "y", "on")

@dataclass(frozen=True)
class Settings:
    llm_mode: str  # "fake" or "real"
    allow_real_llm: bool # saftey switch to ensure that tokens aren't used when they shouldn't be.
    azure_endpoint: str
    azure_api_key: str
    azure_api_version: str
    azure_deployment: str
    azure_timeout_seconds: float

def get_settings() -> Settings:
    mode = os.getenv("LLM_MODE", "fake").strip().lower()
    if mode not in ("fake", "real"):
        raise ValueError(f"Invalid LLM_MODE={mode!r}. Expected 'fake' or 'real'.")

    allow = _truthy(os.getenv("ALLOW_REAL_LLM", "0"))
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").strip()
    api_key = os.getenv("AZURE_OPENAI_API_KEY", "").strip()
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "").strip() or "2024-10-21"
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "").strip()
    timeout = float(os.getenv("AZURE_OPENAI_TIMEOUT_SECONDS", "30"))

    return Settings(
        llm_mode=mode,
        allow_real_llm=allow,
        azure_endpoint=endpoint,
        azure_api_key=api_key,
        azure_api_version=api_version,
        azure_deployment=deployment,
        azure_timeout_seconds=timeout,
    )
