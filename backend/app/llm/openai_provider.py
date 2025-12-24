# backend/app/llm/openai_provider.py
from __future__ import annotations

from typing import Optional

from openai import (
    AsyncAzureOpenAI,
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    PermissionDeniedError,
    NotFoundError,
    RateLimitError,
    BadRequestError,
    InternalServerError,
)

from app.config import Settings
from app.llm.provider_errors import LLMProviderError


def _try_retry_after_seconds(exc: Exception) -> Optional[int]:
    resp = getattr(exc, "response", None)
    headers = getattr(resp, "headers", None) if resp is not None else None
    if not headers:
        return None

    ra = headers.get("retry-after") or headers.get("Retry-After")
    if not ra:
        return None

    try:
        return int(ra)
    except ValueError:
        return None


class AzureOpenAIProvider:
    def __init__(self, settings: Settings):
        if not settings.azure_endpoint:
            raise RuntimeError("AZURE_OPENAI_ENDPOINT is not set.")
        if not settings.azure_api_key:
            raise RuntimeError("AZURE_OPENAI_API_KEY is not set.")
        if not settings.azure_api_version:
            raise RuntimeError("AZURE_OPENAI_API_VERSION is not set.")
        if not settings.azure_deployment:
            raise RuntimeError("AZURE_OPENAI_DEPLOYMENT is not set.")

        self._deployment = settings.azure_deployment
        self._client = AsyncAzureOpenAI(
            azure_endpoint=settings.azure_endpoint,
            api_key=settings.azure_api_key,
            api_version=settings.azure_api_version,
        )
        self._timeout = settings.azure_timeout_seconds

    async def complete(self, prompt: str) -> str:
        try:
            resp = await self._client.chat.completions.create(
                model=self._deployment,
                messages=[{"role": "user", "content": prompt}],
                timeout=self._timeout,
            )
            return resp.choices[0].message.content or ""

        except RateLimitError as e:
            raise LLMProviderError(
                status_code=429,
                code="RATE_LIMIT_EXCEEDED",
                message="Too many requests. Please retry after the specified time.",
                retry_after_seconds=_try_retry_after_seconds(e),
            ) from e

        except APITimeoutError as e:
            raise LLMProviderError(
                status_code=504,
                code="LLM_TIMEOUT",
                message="The LLM request timed out.",
            ) from e

        except APIConnectionError as e:
            raise LLMProviderError(
                status_code=502,
                code="LLM_PROVIDER_FAILURE",
                message="Failed to connect to the upstream LLM provider.",
            ) from e

        except (AuthenticationError, PermissionDeniedError) as e:
            raise LLMProviderError(
                status_code=502,
                code="LLM_PROVIDER_FAILURE",
                message="Upstream authentication/authorization failed.",
            ) from e

        except NotFoundError as e:
            raise LLMProviderError(
                status_code=502,
                code="LLM_PROVIDER_FAILURE",
                message="Upstream model/deployment was not found.",
            ) from e

        except BadRequestError as e:
            raise LLMProviderError(
                status_code=502,
                code="LLM_PROVIDER_FAILURE",
                message="Upstream rejected the request.",
            ) from e

        except InternalServerError as e:
            raise LLMProviderError(
                status_code=502,
                code="LLM_PROVIDER_FAILURE",
                message="Upstream provider encountered an internal error.",
            ) from e
        except Exception as e:
            raise LLMProviderError(
                status_code=502,
                code="LLM_PROVIDER_FAILURE",
                message="Upstream provider request failed.",
            ) from e