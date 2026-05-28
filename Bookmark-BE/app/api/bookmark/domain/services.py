# Standard library imports
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Annotated, List, Optional
from uuid import UUID

# Third-party imports
from dataclass_type_validator import dataclass_validate
from fastapi import Depends, status
from sqlalchemy import exc, select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

# Local application imports
from app.api.bookmark.domain.models import Bookmark, BrokenLinkLog
from app.api.tag.domain.models import Tag
from app.config.db_connection import get_async_db
from app.utils.custom_exception import CustomException
from app.utils.helpers.common_functions import extract_message_from_integrity_error
from app.config.logger import logger


@dataclass_validate(before_post_init=True)
@dataclass(frozen=True)
class BookmarkDataClass:
    user_id: UUID
    url: str
    title: Optional[str] = None
    notes: Optional[str] = None
    is_archived: bool = False
    is_broken: bool = False
    broken_reason: Optional[str] = None
    last_checked_at: Optional[datetime] = None


class BookmarkFactory:
    @staticmethod
    def build_entity(bookmark_data: BookmarkDataClass) -> Bookmark:
        bookmark_dict = asdict(bookmark_data)
        return Bookmark(**bookmark_dict)


class BookmarkDomainServices:
    def __init__(
        self, db_session: Annotated[AsyncSession, Depends(get_async_db)]
    ) -> None:
        self.db_session = db_session

    def get_factory(self) -> type[BookmarkFactory]:
        """
        Get the Bookmark factory instance.
        """
        return BookmarkFactory

    async def create_bookmark(self, bookmark_data: BookmarkDataClass, tags: List[Tag]) -> Bookmark:
        """
        Create a new bookmark in the database.
        """
        try:
            bookmark = self.get_factory().build_entity(bookmark_data)
            bookmark.tags = tags
            self.db_session.add(bookmark)
            await self.db_session.commit()
            await self.db_session.refresh(bookmark)
            return bookmark
        except exc.IntegrityError as ie:
            await self.db_session.rollback()
            logger.error("Integrity Error while creating bookmark: %s", ie)
            message = extract_message_from_integrity_error(str(ie.orig))
            raise CustomException(
                message=message,
                status_code=status.HTTP_409_CONFLICT,
            )
        except exc.SQLAlchemyError as sqe:
            await self.db_session.rollback()
            logger.error("SQLAlchemy Error while creating bookmark: %s", sqe)
            raise sqe

    async def get_bookmarks(
        self,
        user_id: UUID,
        search: Optional[str] = None,
        tag: Optional[str] = None,
        archived: bool = False,
    ) -> List[Bookmark]:
        """
        Retrieve bookmarks matching specific filters.
        """
        query = (
            select(Bookmark)
            .options(selectinload(Bookmark.tags))
            .where(Bookmark.user_id == user_id, Bookmark.is_archived == archived)
        )

        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                or_(
                    Bookmark.title.ilike(search_pattern),
                    Bookmark.notes.ilike(search_pattern),
                )
            )

        if tag:
            query = query.where(Bookmark.tags.any(Tag.name.ilike(tag)))

        query = query.order_by(Bookmark.created_at.desc())
        result = await self.db_session.execute(query)
        return list(result.scalars().all())

    async def get_bookmark_by_id(self, bookmark_id: UUID, user_id: UUID) -> Optional[Bookmark]:
        """
        Get bookmark by ID for a specific user.
        """
        query = (
            select(Bookmark)
            .options(selectinload(Bookmark.tags))
            .where(Bookmark.id == bookmark_id, Bookmark.user_id == user_id)
        )
        result = await self.db_session.execute(query)
        return result.scalars().first()

    async def update_bookmark(
        self, bookmark: Bookmark, bookmark_data: BookmarkDataClass, tags: Optional[List[Tag]] = None
    ) -> Bookmark:
        """
        Update fields of a bookmark and save.
        """
        try:
            bookmark.url = bookmark_data.url
            bookmark.title = bookmark_data.title
            bookmark.notes = bookmark_data.notes
            bookmark.is_archived = bookmark_data.is_archived
            bookmark.is_broken = bookmark_data.is_broken
            bookmark.broken_reason = bookmark_data.broken_reason
            bookmark.last_checked_at = bookmark_data.last_checked_at
            if tags is not None:
                bookmark.tags = tags

            self.db_session.add(bookmark)
            await self.db_session.commit()
            await self.db_session.refresh(bookmark)
            return bookmark
        except exc.SQLAlchemyError as sqe:
            await self.db_session.rollback()
            logger.error("SQLAlchemy Error while updating bookmark: %s", sqe)
            raise sqe

    async def delete_bookmark(self, bookmark: Bookmark) -> None:
        """
        Delete a bookmark from the database.
        """
        try:
            await self.db_session.delete(bookmark)
            await self.db_session.commit()
        except exc.SQLAlchemyError as sqe:
            await self.db_session.rollback()
            logger.error("SQLAlchemy Error while deleting bookmark: %s", sqe)
            raise sqe

    async def log_broken_link_check(
        self, bookmark_id: UUID, status_code: Optional[int], error_message: Optional[str]
    ) -> BrokenLinkLog:
        """
        Log details of a broken link check.
        """
        try:
            log = BrokenLinkLog(
                bookmark_id=bookmark_id,
                error_message=error_message or "",
            )
            self.db_session.add(log)
            await self.db_session.commit()
            return log
        except exc.SQLAlchemyError as sqe:
            await self.db_session.rollback()
            logger.error("SQLAlchemy Error while logging broken link check: %s", sqe)
            raise sqe
