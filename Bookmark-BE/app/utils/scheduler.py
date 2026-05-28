# Third-party imports
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

# Local imports
from app.config.logger import logger
from app.tasks.bookmark_tasks import weekly_broken_link_check_task

# Initialize scheduler
scheduler = AsyncIOScheduler()


def start_scheduler() -> None:
    """
    Start the background task scheduler.
    """
    if not scheduler.running:
        scheduler.start()
        logger.info("Background task scheduler started.")


def shutdown_scheduler() -> None:
    """
    Shut down the background task scheduler.
    """
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Background task scheduler shut down.")


def add_weekly_broken_link_check_task() -> None:
    """
    Register the weekly broken link checking task with the scheduler.
    This task will run every Sunday at midnight (00:00).
    """
    scheduler.add_job(
        weekly_broken_link_check_task,
        trigger=CronTrigger(
            day_of_week="sun",
            hour=0,
            minute=0,
        ),
        id="weekly_broken_link_check",
        name="Weekly broken links verification checker",
        replace_existing=True,
    )
    logger.info("Weekly broken link checker task registered.")
