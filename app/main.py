from fastapi import FastAPI
from routes import alerts

app = FastAPI()

app.include_router(alerts.router)
