from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Sequence


def _truthy(s: str | None) -> bool:
    return (s or "").strip().lower() in ("1", "true", "yes", "y", "on")


def _csv(name: str, default: str) -> list[str]:
    raw = os.getenv(name, default)
    return [x.strip() for x in raw.split(",") if x.strip()]


@dataclass(frozen=True)
class Settings:
    llm_mode: str  # "fake" or "real"
    allow_real_llm: bool  # safety switch to ensure tokens aren't used unexpectedly
    azure_endpoint: str
    azure_api_key: str
    azure_api_version: str
    azure_deployment: str
    azure_timeout_seconds: float

    cors_origins: Sequence[str]
    cors_allow_credentials: bool
    cors_allow_methods: Sequence[str]
    cors_allow_headers: Sequence[str]


def get_settings() -> Settings:
    # ----- App environment -----
    env = os.getenv("ENV", "development").strip().lower()

    # ----- LLM settings -----
    mode = os.getenv("LLM_MODE", "fake").strip().lower()
    if mode not in ("fake", "real"):
        raise ValueError(f"Invalid LLM_MODE={mode!r}. Expected 'fake' or 'real'.")

    allow = _truthy(os.getenv("ALLOW_REAL_LLM", "0"))
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").strip()
    api_key = os.getenv("AZURE_OPENAI_API_KEY", "").strip()
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "").strip() or "2024-10-21"
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "").strip()
    timeout = float(os.getenv("AZURE_OPENAI_TIMEOUT_SECONDS", "30"))

    # ----- CORS settings -----
    raw_origins = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3001,http://127.0.0.1:3001",  # dev default
    )
    cors_origins = [o.strip() for o in raw_origins.split(",") if o.strip()]

    cors_allow_credentials = _truthy(os.getenv("CORS_ALLOW_CREDENTIALS", "0"))
    cors_allow_methods = _csv("CORS_ALLOW_METHODS", "POST,OPTIONS")
    cors_allow_headers = _csv("CORS_ALLOW_HEADERS", "Content-Type")

    # Safety guard: locked-down production expectations
    if env in ("prod", "production"):
        if not cors_origins:
            raise ValueError("CORS_ORIGINS must be set in production.")
        if any(o == "*" for o in cors_origins):
            raise ValueError("CORS_ORIGINS must not include '*' in production.")
        if cors_allow_credentials and any(o == "*" for o in cors_origins):
            # Extra safety: credentials + wildcard is invalid/unsafe
            raise ValueError("CORS_ALLOW_CREDENTIALS=true cannot be used with wildcard origins.")

    return Settings(
        llm_mode=mode,
        allow_real_llm=allow,
        azure_endpoint=endpoint,
        azure_api_key=api_key,
        azure_api_version=api_version,
        azure_deployment=deployment,
        azure_timeout_seconds=timeout,
        cors_origins=cors_origins,
        cors_allow_credentials=cors_allow_credentials,
        cors_allow_methods=cors_allow_methods,
        cors_allow_headers=cors_allow_headers,
    )
