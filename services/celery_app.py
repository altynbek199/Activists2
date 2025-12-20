from celery import Celery
from settings import settings


celery = Celery(
    "services.celery_app",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["services.resize_images"],
    brocker_connection_retry_on_startup=True,
)