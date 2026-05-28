# Standard library imports
from dataclasses import dataclass, asdict
from typing import Annotated, List, Optional
from uuid import UUID

# Third-party imports
from dataclass_type_validator import dataclass_validate
from fastapi import Depends, status
from sqlalchemy import exc, select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

# Local application imports
from app.api.tag.domain.models import Tag
from app.api.bookmark.domain.models import bookmark_tags
from app.config.db_connection import get_async_db
from app.utils.custom_exception import CustomException
from app.utils.helpers.common_functions import extract_message_from_integrity_error
from app.config.logger import logger
from app.utils.messages.custom_response_messages import get_response_message


@dataclass_validate(before_post_init=True)
@dataclass(frozen=True)
class TagDataClass:
    user_id: UUID
    name: str


class TagFactory:
    @staticmethod
    def build_entity(tag_data: TagDataClass) -> Tag:
        tag_dict = asdict(tag_data)
        return Tag(**tag_dict)


class TagDomainServices:
    def __init__(
        self, db_session: Annotated[AsyncSession, Depends(get_async_db)]
    ) -> None:
        self.db_session = db_session

    def get_factory(self) -> type[TagFactory]:
        """
        Get the Tag factory instance.
        """
        return TagFactory

    async def create_tag(self, tag_data: TagDataClass) -> Tag:
        """
        Create a new tag record in the database.
        """
        try:
            tag = self.get_factory().build_entity(tag_data)
            self.db_session.add(tag)
            await self.db_session.commit()
            await self.db_session.refresh(tag)
            return tag
        except exc.IntegrityError as ie:
            await self.db_session.rollback()
            logger.error("Integrity Error while creating tag: %s", ie)
            message = extract_message_from_integrity_error(str(ie.orig))
            raise CustomException(
                message=message,
                status_code=status.HTTP_409_CONFLICT,
            )
        except exc.SQLAlchemyError as sqe:
            await self.db_session.rollback()
            logger.error("SQLAlchemy Error while creating tag: %s", sqe)
            raise sqe

    async def get_tags_by_user(self, user_id: UUID) -> List[Tag]:
        """
        Get all tags created by a specific user.
        """
        query = select(Tag).where(Tag.user_id == user_id).order_by(Tag.name.asc())
        result = await self.db_session.execute(query)
        return list(result.scalars().all())

    async def get_tag_by_name_and_user(self, user_id: UUID, name: str) -> Optional[Tag]:
        """
        Get a specific tag by user and tag name.
        """
        query = select(Tag).where(
            and_(Tag.user_id == user_id, func.lower(Tag.name) == name.lower())
        )
        result = await self.db_session.execute(query)
        return result.scalars().first()

    async def get_tag_by_id_and_user(self, tag_id: UUID, user_id: UUID) -> Optional[Tag]:
        """
        Get a specific tag by ID and user.
        """
        query = select(Tag).where(and_(Tag.id == tag_id, Tag.user_id == user_id))
        result = await self.db_session.execute(query)
        return result.scalars().first()

    async def get_tags_by_ids_and_user(self, tag_ids: List[UUID], user_id: UUID) -> List[Tag]:
        """
        Get list of tags matching tag_ids and user_id.
        """
        query = select(Tag).where(and_(Tag.id.in_(tag_ids), Tag.user_id == user_id))
        result = await self.db_session.execute(query)
        return list(result.scalars().all())

    async def get_or_create_tags_by_names(self, user_id: UUID, names: List[str]) -> List[Tag]:
        """
        Idempotently resolve a list of tag names into Tag database records.
        Creates them if they don't already exist.
        """
        tags = []
        for name in names:
            name_stripped = name.strip()
            if not name_stripped:
                continue
            tag = await self.get_tag_by_name_and_user(user_id, name_stripped)
            if not tag:
                tag_data = TagDataClass(user_id=user_id, name=name_stripped)
                try:
                    tag = self.get_factory().build_entity(tag_data)
                    self.db_session.add(tag)
                    await self.db_session.flush()
                except exc.IntegrityError:
                    await self.db_session.rollback()
                    tag = await self.get_tag_by_name_and_user(user_id, name_stripped)
            tags.append(tag)
        await self.db_session.commit()
        return tags

    async def get_tag_cloud(self, user_id: UUID) -> List[dict]:
        """
        Query tags and get count of bookmarks associated with them.
        """
        query = (
            select(Tag.name, func.count(bookmark_tags.c.bookmark_id).label("count"))
            .outerjoin(bookmark_tags, Tag.id == bookmark_tags.c.tag_id)
            .where(Tag.user_id == user_id)
            .group_by(Tag.name)
            .order_by(func.count(bookmark_tags.c.bookmark_id).desc(), Tag.name.asc())
        )
        result = await self.db_session.execute(query)
        rows = result.all()
        return [{"name": row.name, "count": row.count} for row in rows]
