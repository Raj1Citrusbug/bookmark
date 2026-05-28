# Standard library imports
from typing import Annotated, List

# Third-party imports
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

# Local imports
from app.api.bookmark.domain.models import Bookmark
from app.api.auth.domain.models import User
from app.config.db_connection import get_async_db


class AdminDomainServices:
    def __init__(
        self, db_session: Annotated[AsyncSession, Depends(get_async_db)]
    ) -> None:
        self.db_session = db_session

    async def get_all_broken_bookmarks(self) -> List[Bookmark]:
        """
        Retrieve all broken bookmarks across the entire system.
        Loads the owner relationship for reporting.
        """
        query = (
            select(Bookmark)
            .options(selectinload(Bookmark.user))
            .where(Bookmark.is_broken == True)
            .order_by(Bookmark.last_checked_at.desc())
        )
        result = await self.db_session.execute(query)
        return list(result.scalars().all())