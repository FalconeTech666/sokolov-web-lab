from fastapi import FastAPI
from fastapi_app.routers import tasks
from fastapi_app.routers import validator
from fastapi_app.routers import news
from fastapi_app.routers import reminders

fastapi_app = FastAPI(
    title="Sokol Web Lab API",
    description="Учебные API (FastAPI).",
    version="1.0.0",
    root_path="/fastapi"
)

fastapi_app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
fastapi_app.include_router(validator.router, prefix="/validator", tags=["validator"])
fastapi_app.include_router(news.router, prefix="/news", tags=["news"])
fastapi_app.include_router(reminders.router, prefix="/reminders", tags=["reminders"])


