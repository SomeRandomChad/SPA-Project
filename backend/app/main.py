"""Main application"""
from fastapi import FastAPI

from app.errors.register import register_exception_handlers
from app.routes.rephrase import router as rephrase_router
from dotenv import load_dotenv
load_dotenv()

def create_app() -> FastAPI:
    app = FastAPI()
    register_exception_handlers(app)

    app.include_router(rephrase_router)
    return app

app = create_app()