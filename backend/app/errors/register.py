from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from .handlers import request_validation_exception_handler


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
