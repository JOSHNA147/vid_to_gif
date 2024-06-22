from celery import Celery
from config import Config

def make_celery(app_name=__name__):
    return Celery(
        app_name,
        broker=Config.CELERY_BROKER_URL,
        backend=Config.CELERY_RESULT_BACKEND
    )

celery = make_celery()

import tasks
