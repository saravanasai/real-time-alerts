import logging
from fastapi import FastAPI
from .routes import alerts
from .routes import auth
from app.middleware.request_logger_middleware import RequestLoggerMiddleware

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


app = FastAPI()

app.add_middleware(RequestLoggerMiddleware)

app.include_router(alerts.router)
app.include_router(auth.router)
