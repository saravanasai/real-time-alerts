import os
from kombu import Queue
from celery.schedules import crontab
from sqlalchemy import create_engine
from dotenv import load_dotenv


load_dotenv()


class Config:
    POSTGRES_USER = os.getenv('POSTGRES_USER', 'root')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'root')
    POSTGRES_DB = os.getenv('POSTGRES_DB', 'alerts_db')
    POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
    POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')
    CONNECTION_URL = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'

    # Redis Configuration
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = int(os.getenv('REDIS_DB', 0))

    # Celery Configuration
    CELERY_BROKER_URL = os.getenv(
        'CELERY_BROKER_URL', 'amqp://root:root@localhost:5672//')
    CELERY_RESULT_BACKEND = os.getenv(
        'CELERY_RESULT_BACKEND', 'rpc://')

    # JWT Configuration
    SECRET_KEY = os.getenv(
        "SECRET_KEY", "b0ab05f487cf0877b29ff510bb8c1222")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    REFRESH_TOKEN_EXPIRE_DAYS = 7

    @property
    def postgresql_engine(self):
        return create_engine(f'postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}')

    def connection_url(self) -> str:
        return f'postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}'


class CeleryConfig:

    broker_url: str = os.getenv(
        "CELERY_BROKER_URL",
        "amqp://root:root@rabbitmq:5672//"
    )
    result_backend: str = os.getenv(
        "CELERY_RESULT_BACKEND",
        "rpc://"
    )
    result_expires = 600
    task_default_queue: str = "default"

    task_create_missing_queues: bool = True

    # Define task queues with priority names
    task_queues: list = [
        Queue("default"),
        Queue("high_priority"),
        Queue("medium_priority"),
        Queue("low_priority"),
    ]

    task_routes = {
        "send_alert": {
            "queue": "high_priority",
        },
    }

    beat_schedule: dict = {

    }

    # imports = "src.tasks"
    broker_connection_retry_on_startup = True
    timezone = "Asia/Kolkata"


celery_settings = Config()
celery_settings = CeleryConfig()
