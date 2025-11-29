from celery import Celery
from app.config import celery_settings


def create_celery_app() -> Celery:
    """
    Create and configure Celery application
    """
    # Create a NEW Celery instance (not using current_app)
    celery_app = Celery("awesome_alerts")  # Give it a name

    # Load configuration from your CeleryConfig class
    celery_app.config_from_object(celery_settings)

    return celery_app


# Create the Celery app instance
celery_app = create_celery_app()
