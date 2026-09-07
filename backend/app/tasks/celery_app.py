"""Celery application and periodic task scheduler configuration."""

try:
    from celery import Celery
    from celery.schedules import crontab
    CELERY_AVAILABLE = True
except ImportError:
    Celery = object
    crontab = lambda **kwargs: None
    CELERY_AVAILABLE = False

from app.core.config import settings
from app.core.logging import logger

if CELERY_AVAILABLE:
    celery = Celery(
        "fieldmind",
        broker=settings.CELERY_BROKER_URL,
        backend=settings.CELERY_RESULT_BACKEND,
        include=["app.tasks.rewards_tasks"]
    )

    celery.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
        beat_schedule={
            "audit-100-job-monthly-rewards": {
                "task": "app.tasks.rewards_tasks.audit_monthly_technician_rewards",
                # Midnight on the 1st of every month
                "schedule": crontab(minute=0, hour=0, day_of_month=1),
            },
        }
    )
else:
    class DummyCelery:
        def task(self, *args, **kwargs):
            def decorator(f):
                return f
            return decorator
    celery = DummyCelery()
