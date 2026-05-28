from app.config.logger import logger
from app.config.settings import app_settings


class EmailService:
    """
    Mock Email Service simulating email sends.
    """

    async def send_welcome_email(self, user_email: str, name: str):
        """
        Simulate sending a welcome email to a newly registered user.
        """
        logger.info(
            f"Sending Welcome Email to {user_email} (Name: {name}) from {app_settings.FROM_EMAIL}"
        )
        print(f"📧 [Email System] Welcome email successfully sent to {user_email}.")

    async def send_weekly_broken_links_summary(self, user_email: str, broken_bookmarks: list):
        """
        Simulate sending a weekly summary email containing user's broken bookmarks.
        """
        logger.info(
            f"Sending Broken Links Summary to {user_email} with {len(broken_bookmarks)} broken link(s)."
        )
        print(
            f"📧 [Email System] Weekly broken links summary sent to {user_email}. "
            f"Found {len(broken_bookmarks)} broken bookmarks."
        )


email_service = EmailService()