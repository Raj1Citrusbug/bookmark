# Standard library imports
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Annotated, List, Optional, Tuple
from uuid import UUID

# Third-party imports
from dataclass_type_validator import dataclass_validate
from fastapi import Depends, status
from sqlalchemy import exc, select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

# Local application imports
from app.api.bookmark.domain.models import Bookmark, BrokenLinkLog
from app.api.tag.domain.models import Tag
from app.config.db_connection import get_async_db
from app.utils.custom_exception import CustomException
from app.utils.messages.custom_response_messages import get_response_message
from app.utils.helpers.common_functions import extract_message_from_integrity_error
from app.config.logger import logger
from app.schema.bookmark.request_schema import BookmarkQueryParamsSchema
from app.utils.enums import SortOrder


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

    async def create_bookmark(
        self, bookmark_data: BookmarkDataClass, tags: List[Tag]
    ) -> Bookmark:
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
        query_params: BookmarkQueryParamsSchema,
    ) -> Tuple[List[Bookmark], int]:
        """
        Retrieve bookmarks matching specific filters, with pagination.
        """
        filters = set()
        filters.add(Bookmark.user_id == user_id)

        if query_params.search:
            search_pattern = f"%{query_params.search}%"
            filters.add(
                or_(
                    Bookmark.title.ilike(search_pattern),
                    Bookmark.notes.ilike(search_pattern),
                )
            )

        if query_params.tag:
            filters.add(Bookmark.tags.any(Tag.name.ilike(query_params.tag)))

        if query_params.archived is not None:
            filters.add(Bookmark.is_archived == query_params.archived)

        base_query = (
            select(Bookmark, func.count().over().label("total_count"))
            .options(selectinload(Bookmark.tags))
            .where(*filters)
        )

        order_by = (
            Bookmark.created_at.asc()
            if query_params.sort_order == SortOrder.ASC
            else Bookmark.created_at.desc()
        )

        # Apply pagination and order
        paginated_query = (
            base_query.order_by(order_by)
            .offset((query_params.page - 1) * query_params.limit)
            .limit(query_params.limit)
        )
        result = await self.db_session.execute(paginated_query)
        rows = result.all()

        if not rows:
            return [], 0

        bookmarks = [row[0] for row in rows]
        total_count = int(rows[0].total_count)
        return bookmarks, total_count

    async def get_bookmark_by_id(
        self, bookmark_id: UUID, user_id: UUID
    ) -> Optional[Bookmark]:
        """
        Get bookmark by ID for a specific user.
        """
        query = (
            select(Bookmark)
            .options(selectinload(Bookmark.tags))
            .where(Bookmark.id == bookmark_id, Bookmark.user_id == user_id)
        )
        result = await self.db_session.execute(query)
        bookmark = result.scalars().first()
        if not bookmark:
            raise CustomException(
                message=get_response_message("not_found", "Bookmark"),
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return bookmark

    async def partial_update_bookmark(
        self, bookmark: Bookmark, update_dict: dict
    ) -> None:
        """
        Update an existing bookmark.

        Args:
            bookmark (Bookmark): The bookmark entity to update.
            update_dict (dict): The data to update.

        Returns:
            None

        Raises:
            exc.SQLAlchemyError: If a database error occurs.
        """
        try:
            for key, value in update_dict.items():
                setattr(bookmark, key, value)
            await self.db_session.commit()
            await self.db_session.refresh(bookmark)
            return None
        except exc.SQLAlchemyError as sqe:
            await self.db_session.rollback()
            logger.error("SQLAlchemy Error while updating bookmark: %s", sqe)
            raise sqe
        except Exception as e:
            await self.db_session.rollback()
            logger.error("General Exception while updating bookmark: %s", e)
            raise e

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
        self,
        bookmark_id: UUID,
        status_code: Optional[int],
        error_message: Optional[str],
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
