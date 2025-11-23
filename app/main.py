from fastapi import FastAPI
from .routes import alerts
from .routes import auth

app = FastAPI()

app.include_router(alerts.router)
app.include_router(auth.router)
