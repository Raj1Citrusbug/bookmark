from celery import Celery
from celery.schedules import crontab
from app.config.settings import app_settings

# Initialize the Celery application using Redis configured in settings
celery_app = Celery(
    "bookmark_manager",
    broker=app_settings.REDIS_URL,
    backend=app_settings.REDIS_URL,
)

celery_app.conf.update(
    task_track_started=True,
    timezone="UTC",
    enable_utc=True,
    imports=[
        "app.tasks.bookmark_tasks",
    ],
)

# Autodiscover tasks inside app/tasks
celery_app.autodiscover_tasks(["app"])

# Configure the weekly broken links check schedule
celery_app.conf.beat_schedule = {
    # NOTE: Uncomment the following for production schedule (runs every Sunday at midnight)
    # "weekly-broken-link-check": {
    #     "task": "app.tasks.bookmark_tasks.weekly_broken_link_check_task",
    #     "schedule": crontab(day_of_week="sun", hour=0, minute=0),
    # },
    # Test schedule: runs every minute
    "every-minute-broken-link-check": {
        "task": "app.tasks.bookmark_tasks.weekly_broken_link_check_task",
        "schedule": crontab(minute="*"),
    },
}
