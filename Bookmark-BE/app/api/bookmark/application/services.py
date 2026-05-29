# Standard library imports
from typing import List, Tuple
from uuid import UUID

# Third-party imports
from fastapi import Depends, status

# Local application imports
from app.api.bookmark.domain.services import BookmarkDomainServices, BookmarkDataClass
from app.api.tag.domain.services import TagDomainServices
from app.api.auth.domain.models import User
from app.schema.bookmark.request_schema import (
    BookmarkCreateRequestSchema,
    BookmarkUpdateRequestSchema,
    BookmarkQueryParamsSchema,
)
from app.schema.bookmark.response_schema import BookmarkDetailDataSchema
from app.utils.custom_exception import CustomException
from app.tasks.bookmark_tasks import fetch_title_task


class BookmarkAppServices:
    def __init__(
        self,
        bookmark_domain_services: BookmarkDomainServices = Depends(
            BookmarkDomainServices
        ),
        tag_domain_services: TagDomainServices = Depends(TagDomainServices),
    ) -> None:
        self.bookmark_domain_services = bookmark_domain_services
        self.tag_domain_services = tag_domain_services

    async def create_bookmark(
        self,
        current_user: User,
        bookmark_data: BookmarkCreateRequestSchema,
    ) -> None:
        """
        Create a new bookmark, map its tags, and schedule background title scraping if needed.
        """
        tags = []
        if bookmark_data.tags:
            tags = await self.tag_domain_services.get_tags_by_ids_and_user(
                bookmark_data.tags, current_user.id
            )
            if len(tags) != len(set(bookmark_data.tags)):
                raise CustomException(
                    message="Some tag IDs are not found",
                    status_code=status.HTTP_404_NOT_FOUND,
                )

        title = bookmark_data.title

        data = BookmarkDataClass(
            user_id=current_user.id,
            url=bookmark_data.url,
            title=title,
            notes=bookmark_data.notes,
            is_archived=False,
            is_broken=False,
        )

        bookmark = await self.bookmark_domain_services.create_bookmark(data, tags)

        if not title:
            fetch_title_task.delay(str(bookmark.id))

        return None

    async def get_bookmarks(
        self,
        current_user: User,
        query_params: BookmarkQueryParamsSchema,
    ) -> Tuple[List[BookmarkDetailDataSchema], int]:
        """
        Browse user's saved bookmarks with search, tag filters and pagination.
        """
        bookmarks, total_count = await self.bookmark_domain_services.get_bookmarks(
            current_user.id,
            query_params,
        )
        return bookmarks, total_count

    async def get_bookmark(
        self, current_user: User, bookmark_id: UUID
    ) -> BookmarkDetailDataSchema:
        """
        Retrieve details of a specific bookmark.
        """
        bookmark = await self.bookmark_domain_services.get_bookmark_by_id(
            bookmark_id, current_user.id
        )
        return bookmark

    async def update_bookmark(
        self,
        current_user: User,
        bookmark_id: UUID,
        bookmark_data: BookmarkUpdateRequestSchema,
    ) -> None:
        """
        Modify details of an existing bookmark.
        """
        bookmark = await self.bookmark_domain_services.get_bookmark_by_id(
            bookmark_id, current_user.id
        )

        update_data = bookmark_data.model_dump(exclude_unset=True)

        if bookmark_data.tags is not None:
            tags = await self.tag_domain_services.get_tags_by_ids_and_user(
                bookmark_data.tags, current_user.id
            )
            if len(tags) != len(set(bookmark_data.tags)):
                raise CustomException(
                    message="Some tag IDs are not found",
                    status_code=status.HTTP_404_NOT_FOUND,
                )
            update_data["tags"] = tags

        await self.bookmark_domain_services.partial_update_bookmark(
            bookmark, update_data
        )
        return None

    async def delete_bookmark(self, current_user: User, bookmark_id: UUID) -> None:
        """
        Permanently delete a bookmark (hard delete).
        """
        bookmark = await self.bookmark_domain_services.get_bookmark_by_id(
            bookmark_id, current_user.id
        )

        await self.bookmark_domain_services.delete_bookmark(bookmark)

    async def archive_bookmark(
        self, current_user: User, bookmark_id: UUID
    ) -> BookmarkDetailDataSchema:
        """
        Toggle the archive status of a bookmark.
        """
        bookmark = await self.bookmark_domain_services.get_bookmark_by_id(
            bookmark_id, current_user.id
        )

        update_data = {"is_archived": not bookmark.is_archived}
        await self.bookmark_domain_services.partial_update_bookmark(
            bookmark, update_data
        )
        return None

    async def refetch_title(self, current_user: User, bookmark_id: UUID) -> None:
        """
        Force refetch title extraction from the webpage in the background.
        """
        bookmark = await self.bookmark_domain_services.get_bookmark_by_id(
            bookmark_id, current_user.id
        )

        fetch_title_task.delay(str(bookmark.id))
