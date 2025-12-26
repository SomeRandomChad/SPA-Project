# backend/app/errors/register.py
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from app.llm.parse import ModelOutputError
from app.llm.provider_errors import LLMProviderError
from .handlers import (
    llm_provider_exception_handler,
    model_output_exception_handler,
    request_validation_exception_handler,
)


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
    app.add_exception_handler(ModelOutputError, model_output_exception_handler)
    app.add_exception_handler(LLMProviderError, llm_provider_exception_handler)
