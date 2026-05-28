# Standard library imports
from typing import List, Optional
from uuid import UUID

# Third-party imports
from fastapi import Depends, status, BackgroundTasks

# Local application imports
from app.api.bookmark.domain.services import BookmarkDomainServices, BookmarkDataClass
from app.api.bookmark.domain.models import Bookmark
from app.api.tag.domain.services import TagDomainServices
from app.api.auth.domain.models import User
from app.schema.bookmark.request_schema import BookmarkCreateRequestSchema, BookmarkUpdateRequestSchema
from app.schema.bookmark.response_schema import BookmarkDetailDataSchema
from app.utils.custom_exception import CustomException
from app.utils.messages.custom_response_messages import get_response_message


class BookmarkAppServices:
    def __init__(
        self,
        bookmark_domain_services: BookmarkDomainServices = Depends(BookmarkDomainServices),
        tag_domain_services: TagDomainServices = Depends(TagDomainServices),
    ) -> None:
        self.bookmark_domain_services = bookmark_domain_services
        self.tag_domain_services = tag_domain_services

    async def create_bookmark(
        self, current_user: User, bookmark_data: BookmarkCreateRequestSchema, background_tasks: BackgroundTasks
    ) -> BookmarkDetailDataSchema:
        """
        Create a new bookmark, map its tags, and schedule background title scraping if needed.
        """
        tags = []
        if bookmark_data.tags:
            tags = await self.tag_domain_services.get_tags_by_ids_and_user(bookmark_data.tags, current_user.id)
            if len(tags) != len(bookmark_data.tags):
                raise CustomException(
                    message=get_response_message("not_found", "One or more tags"),
                    status_code=status.HTTP_404_NOT_FOUND,
                )

        title = bookmark_data.title.strip() if bookmark_data.title else ""

        data = BookmarkDataClass(
            user_id=current_user.id,
            url=bookmark_data.url.strip(),
            title=title,
            notes=bookmark_data.notes.strip() if bookmark_data.notes else None,
            is_archived=False,
            is_broken=False,
        )

        bookmark = await self.bookmark_domain_services.create_bookmark(data, tags)

        if not title:
            from app.tasks.bookmark_tasks import fetch_title_task
            background_tasks.add_task(fetch_title_task, str(bookmark.id))

        return BookmarkDetailDataSchema.model_validate(bookmark)

    async def get_bookmarks(
        self,
        current_user: User,
        search: Optional[str] = None,
        tag: Optional[str] = None,
        archived: bool = False,
    ) -> List[BookmarkDetailDataSchema]:
        """
        Browse user's saved bookmarks with search and tag filters.
        """
        bookmarks = await self.bookmark_domain_services.get_bookmarks(
            current_user.id, search=search, tag=tag, archived=archived
        )
        return [BookmarkDetailDataSchema.model_validate(b) for b in bookmarks]

    async def get_bookmark(self, current_user: User, bookmark_id: UUID) -> BookmarkDetailDataSchema:
        """
        Retrieve details of a specific bookmark.
        """
        bookmark = await self.bookmark_domain_services.get_bookmark_by_id(
            bookmark_id, current_user.id
        )
        if not bookmark:
            raise CustomException(
                message=get_response_message("not_found", "Bookmark"),
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return BookmarkDetailDataSchema.model_validate(bookmark)

    async def update_bookmark(
        self, current_user: User, bookmark_id: UUID, bookmark_data: BookmarkUpdateRequestSchema
    ) -> BookmarkDetailDataSchema:
        """
        Modify details of an existing bookmark.
        """
        bookmark = await self.bookmark_domain_services.get_bookmark_by_id(
            bookmark_id, current_user.id
        )
        if not bookmark:
            raise CustomException(
                message=get_response_message("not_found", "Bookmark"),
                status_code=status.HTTP_404_NOT_FOUND,
            )

        tags = None
        if bookmark_data.tags is not None:
            tags = await self.tag_domain_services.get_tags_by_ids_and_user(bookmark_data.tags, current_user.id)
            if len(tags) != len(bookmark_data.tags):
                raise CustomException(
                    message=get_response_message("not_found", "One or more tags"),
                    status_code=status.HTTP_404_NOT_FOUND,
                )

        url = bookmark_data.url.strip() if bookmark_data.url is not None else bookmark.url
        title = bookmark_data.title.strip() if bookmark_data.title is not None else bookmark.title
        notes = bookmark_data.notes.strip() if bookmark_data.notes is not None else bookmark.notes

        data = BookmarkDataClass(
            user_id=bookmark.user_id,
            url=url,
            title=title,
            notes=notes,
            is_archived=bookmark.is_archived,
            is_broken=bookmark.is_broken,
            broken_reason=bookmark.broken_reason,
            last_checked_at=bookmark.last_checked_at,
        )
        updated = await self.bookmark_domain_services.update_bookmark(bookmark, data, tags)
        return BookmarkDetailDataSchema.model_validate(updated)

    async def delete_bookmark(self, current_user: User, bookmark_id: UUID) -> None:
        """
        Permanently delete a bookmark (hard delete).
        """
        bookmark = await self.bookmark_domain_services.get_bookmark_by_id(
            bookmark_id, current_user.id
        )
        if not bookmark:
            raise CustomException(
                message=get_response_message("not_found", "Bookmark"),
                status_code=status.HTTP_404_NOT_FOUND,
            )
        await self.bookmark_domain_services.delete_bookmark(bookmark)

    async def archive_bookmark(self, current_user: User, bookmark_id: UUID) -> BookmarkDetailDataSchema:
        """
        Hide a bookmark by moving it to the archive.
        """
        bookmark = await self.bookmark_domain_services.get_bookmark_by_id(
            bookmark_id, current_user.id
        )
        if not bookmark:
            raise CustomException(
                message=get_response_message("not_found", "Bookmark"),
                status_code=status.HTTP_404_NOT_FOUND,
            )

        data = BookmarkDataClass(
            user_id=bookmark.user_id,
            url=bookmark.url,
            title=bookmark.title,
            notes=bookmark.notes,
            is_archived=True,
            is_broken=bookmark.is_broken,
            broken_reason=bookmark.broken_reason,
            last_checked_at=bookmark.last_checked_at,
        )
        updated = await self.bookmark_domain_services.update_bookmark(bookmark, data)
        return BookmarkDetailDataSchema.model_validate(updated)

    async def unarchive_bookmark(self, current_user: User, bookmark_id: UUID) -> BookmarkDetailDataSchema:
        """
        Restore an archived bookmark back to the main list.
        """
        bookmark = await self.bookmark_domain_services.get_bookmark_by_id(
            bookmark_id, current_user.id
        )
        if not bookmark:
            raise CustomException(
                message=get_response_message("not_found", "Bookmark"),
                status_code=status.HTTP_404_NOT_FOUND,
            )

        data = BookmarkDataClass(
            user_id=bookmark.user_id,
            url=bookmark.url,
            title=bookmark.title,
            notes=bookmark.notes,
            is_archived=False,
            is_broken=bookmark.is_broken,
            broken_reason=bookmark.broken_reason,
            last_checked_at=bookmark.last_checked_at,
        )
        updated = await self.bookmark_domain_services.update_bookmark(bookmark, data)
        return BookmarkDetailDataSchema.model_validate(updated)

    async def refetch_title(self, current_user: User, bookmark_id: UUID, background_tasks: BackgroundTasks) -> None:
        """
        Force refetch title extraction from the webpage in the background.
        """
        bookmark = await self.bookmark_domain_services.get_bookmark_by_id(
            bookmark_id, current_user.id
        )
        if not bookmark:
            raise CustomException(
                message=get_response_message("not_found", "Bookmark"),
                status_code=status.HTTP_404_NOT_FOUND,
            )

        from app.tasks.bookmark_tasks import fetch_title_task
        background_tasks.add_task(fetch_title_task, str(bookmark.id))
