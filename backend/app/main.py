from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.config import get_settings
from app.errors.register import register_exception_handlers
from app.routes.rephrase import router as rephrase_router

load_dotenv()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=list(settings.cors_allow_methods),
        allow_headers=list(settings.cors_allow_headers),
        expose_headers=["Content-Type"],
    )

    register_exception_handlers(app)
    app.include_router(rephrase_router)
    return app


app = create_app()