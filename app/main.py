import logging
from fastapi import FastAPI

from app.celery_app import celery_app
from .routes import alerts
from .routes import auth
from app.middleware.request_logger_middleware import RequestLoggerMiddleware

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(title="Awesome Alerts API", version="1.0")

app.add_middleware(RequestLoggerMiddleware)

app.include_router(alerts.router)
app.include_router(auth.router)

app.state.celery_app = celery_app

celery = celery_app
