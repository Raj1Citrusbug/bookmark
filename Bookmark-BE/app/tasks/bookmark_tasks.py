# Standard library imports
import asyncio
import httpx

# Third-party imports
from datetime import datetime, UTC, timedelta
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from celery import shared_task

# Local application imports
from app.config.db_connection import get_async_engine
from app.api.bookmark.domain.models import Bookmark, BrokenLinkLog
from app.api.auth.domain.models import User
from app.api.tag.domain.models import Tag
from app.config.db_connection import AsyncSessionLocal
from app.config.logger import logger

# Set a standard User-Agent to prevent scrapers from being blocked
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


@shared_task(name="app.tasks.bookmark_tasks.fetch_title_task")
def fetch_title_task(bookmark_id: str):
    """
    Celery task wrapper for scraping webpage titles.
    """
    asyncio.run(_fetch_title_task_async(bookmark_id))


async def _fetch_title_task_async(bookmark_id: str):
    """
    Scrapes a webpage to extract its <title> and updates the bookmark.
    """
    try:
        async with AsyncSessionLocal() as session:
            try:
                # Find bookmark
                query = select(Bookmark).where(Bookmark.id == bookmark_id)
                result = await session.execute(query)
                bookmark = result.scalars().first()

                if not bookmark:
                    logger.warning(
                        f"Bookmark {bookmark_id} not found for title scraping."
                    )
                    return

                logger.info(
                    f"Scraping title for bookmark {bookmark.id} ({bookmark.url})"
                )

                async with httpx.AsyncClient(
                    headers=HEADERS, follow_redirects=True, timeout=10.0
                ) as client:
                    response = await client.get(bookmark.url)

                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, "html.parser")
                        title_tag = soup.find("title")

                        if title_tag and title_tag.string:
                            bookmark.title = title_tag.string.strip()
                        else:
                            parsed_url = urlparse(bookmark.url)
                            bookmark.title = parsed_url.netloc or bookmark.url
                    else:
                        parsed_url = urlparse(bookmark.url)
                        bookmark.title = parsed_url.netloc or bookmark.url

                session.add(bookmark)
                await session.commit()
                logger.info(
                    f"Updated title for bookmark {bookmark.id} to '{bookmark.title}'"
                )

            except Exception as e:
                logger.error(
                    f"Error scraping title for bookmark {bookmark_id}: {str(e)}"
                )
                try:
                    query = select(Bookmark).where(Bookmark.id == bookmark_id)
                    res = await session.execute(query)
                    bm = res.scalars().first()
                    if bm:
                        parsed_url = urlparse(bm.url)
                        bm.title = parsed_url.netloc or bm.url
                        session.add(bm)
                        await session.commit()
                except Exception as ex:
                    logger.error(f"Fallback title update failed: {str(ex)}")
    finally:
        await get_async_engine().dispose()


@shared_task(name="app.tasks.bookmark_tasks.weekly_broken_link_check_task")
def weekly_broken_link_check_task():
    """
    Celery task wrapper for checking broken links.
    """
    asyncio.run(_weekly_broken_link_check_task_async())


async def _weekly_broken_link_check_task_async():
    """
    Automatically checks for broken URLs.
    Checks bookmarks not verified in the last 7 days.
    """
    try:
        async with AsyncSessionLocal() as session:
            time_threshold = datetime.now(UTC) - timedelta(days=7)
            query = (
                select(Bookmark)
                .options(selectinload(Bookmark.user))
                .where(
                    (Bookmark.last_checked_at == None)
                    | (Bookmark.last_checked_at < time_threshold)
                )
            )
            result = await session.execute(query)
            bookmarks = result.scalars().all()

            logger.info(
                f"Starting broken link verification for {len(bookmarks)} bookmarks."
            )

            user_broken_links = {}

            async with httpx.AsyncClient(
                headers=HEADERS, follow_redirects=True, timeout=10.0
            ) as client:
                for bookmark in bookmarks:
                    is_broken = False
                    broken_reason = None
                    status_code = None
                    error_message = None

                    try:
                        try:
                            response = await client.head(bookmark.url)
                            status_code = response.status_code
                            if response.status_code >= 400:
                                response = await client.get(bookmark.url)
                                status_code = response.status_code
                        except httpx.HTTPStatusError as hse:
                            status_code = hse.response.status_code
                            response = hse.response

                        if status_code and status_code >= 400:
                            is_broken = True
                            broken_reason = f"HTTP Error {status_code}"
                            error_message = (
                                f"Webpage returned status code {status_code}"
                            )
                        else:
                            is_broken = False

                    except httpx.ConnectTimeout:
                        is_broken = True
                        broken_reason = "Timeout"
                        error_message = "Connection timed out after 10 seconds."
                    except httpx.ConnectError:
                        is_broken = True
                        broken_reason = "DNS Failure"
                        error_message = (
                            "Could not resolve hostname / DNS lookup failure."
                        )
                    except Exception as e:
                        is_broken = True
                        broken_reason = "Error"
                        error_message = str(e)

                    bookmark.is_broken = is_broken
                    bookmark.broken_reason = broken_reason if is_broken else None
                    bookmark.last_checked_at = datetime.now(UTC)
                    session.add(bookmark)

                    check_log = BrokenLinkLog(
                        bookmark_id=bookmark.id,
                        error_message=(
                            error_message if is_broken else "Working perfectly"
                        ),
                    )
                    session.add(check_log)

                    if is_broken and bookmark.user:
                        user_email = bookmark.user.email
                        if user_email not in user_broken_links:
                            user_broken_links[user_email] = []
                        user_broken_links[user_email].append(bookmark)

            await session.commit()
            logger.info("Broken link verification completed.")

    except Exception as e:
        logger.error(f"Weekly broken link task failed: {str(e)}")
    finally:
        await get_async_engine().dispose()


# NOTE: To run the Celery worker, use the following command in your terminal at that time in this only for testing purpose and later after this will be removed
# python -m celery -A app.config.celery_app.celery_app worker --loglevel=info -P solo
# python -m celery -A app.config.celery_app.celery_app beat --loglevel=info