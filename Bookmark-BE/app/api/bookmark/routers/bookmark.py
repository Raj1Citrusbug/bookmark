# Standard library imports
from typing import Annotated, Optional
from uuid import UUID

# Third-party imports
from fastapi import APIRouter, Depends, status, Query, BackgroundTasks

# Local imports
from app.schema.bookmark.request_schema import (
    BookmarkCreateRequestSchema,
    BookmarkUpdateRequestSchema,
)
from app.schema.bookmark.response_schema import (
    BookmarkResponseSchema,
    BookmarkListResponseSchema,
)
from app.schema.base import BaseResponseSchema
from app.api.bookmark.application.services import BookmarkAppServices
from app.api.auth.domain.models import User
from app.utils.middleware.auth_middleware import get_current_user
from app.utils.response_handler import ResponseHandler
from app.utils.messages.custom_response_messages import get_response_message

router = APIRouter(prefix="/bookmarks", tags=["Bookmarks"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=BaseResponseSchema,
)
async def create_bookmark(
    bookmark_data: BookmarkCreateRequestSchema,
    background_tasks: BackgroundTasks,
    current_user: Annotated[User, Depends(get_current_user)],
    bookmark_app_service: Annotated[BookmarkAppServices, Depends(BookmarkAppServices)],
) -> BaseResponseSchema:
    """
    Save a new bookmark. If the title is omitted, it will be automatically fetched in the background.
    """
    result = await bookmark_app_service.create_bookmark(
        current_user, bookmark_data, background_tasks
    )
    return ResponseHandler.success(
        message=get_response_message("create_success", "Bookmark"),
        data=result,
    )


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=BookmarkListResponseSchema,
)
async def get_bookmarks(
    current_user: Annotated[User, Depends(get_current_user)],
    bookmark_app_service: Annotated[BookmarkAppServices, Depends(BookmarkAppServices)],
    search: Optional[str] = Query(default=None, description="Search by title or notes"),
    tag: Optional[str] = Query(default=None, description="Filter by tag name"),
    archived: bool = Query(default=False, description="Filter by archived status"),
) -> BookmarkListResponseSchema:
    """
    Browse user's saved bookmarks with search and tag filters.
    """
    result = await bookmark_app_service.get_bookmarks(
        current_user, search=search, tag=tag, archived=archived
    )
    return ResponseHandler.success_listing(
        message=get_response_message("detail_success", "Bookmarks"),
        data=result,
        count=len(result),
    )


@router.get(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=BookmarkResponseSchema,
)
async def get_bookmark(
    id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    bookmark_app_service: Annotated[BookmarkAppServices, Depends(BookmarkAppServices)],
) -> BookmarkResponseSchema:
    """
    Retrieve details of a specific bookmark.
    """
    result = await bookmark_app_service.get_bookmark(current_user, id)
    return ResponseHandler.success(
        message=get_response_message("detail_success", "Bookmark"),
        data=result,
    )


@router.patch(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponseSchema,
)
async def update_bookmark(
    id: UUID,
    bookmark_data: BookmarkUpdateRequestSchema,
    current_user: Annotated[User, Depends(get_current_user)],
    bookmark_app_service: Annotated[BookmarkAppServices, Depends(BookmarkAppServices)],
):
    """
    Modify details of an existing bookmark.
    """
    await bookmark_app_service.update_bookmark(current_user, id, bookmark_data)
    return ResponseHandler.success(
        message=get_response_message("update_success", "Bookmark"),
    )


@router.delete(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponseSchema,
)
async def delete_bookmark(
    id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    bookmark_app_service: Annotated[BookmarkAppServices, Depends(BookmarkAppServices)],
):
    """
    Permanently delete a bookmark (hard delete).
    """
    await bookmark_app_service.delete_bookmark(current_user, id)
    return ResponseHandler.success(
        message=get_response_message("delete_success", "Bookmark"),
    )


@router.patch(
    "/{id}/archive",
    status_code=status.HTTP_200_OK,
    response_model=BookmarkResponseSchema,
)
async def archive_bookmark(
    id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    bookmark_app_service: Annotated[BookmarkAppServices, Depends(BookmarkAppServices)],
):
    """
    Hide a bookmark by moving it to the archive.
    """
    result = await bookmark_app_service.archive_bookmark(current_user, id)
    return ResponseHandler.success(
        message=get_response_message("update_success", "Bookmark archived status"),
        data=result,
    )


@router.patch(
    "/{id}/unarchive",
    status_code=status.HTTP_200_OK,
    response_model=BookmarkResponseSchema,
)
async def unarchive_bookmark(
    id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    bookmark_app_service: Annotated[BookmarkAppServices, Depends(BookmarkAppServices)],
):
    """
    Restore an archived bookmark back to the main list.
    """
    result = await bookmark_app_service.unarchive_bookmark(current_user, id)
    return ResponseHandler.success(
        message=get_response_message("update_success", "Bookmark archived status"),
        data=result,
    )


@router.post(
    "/{id}/refetch-title",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=BaseResponseSchema,
)
async def refetch_title(
    id: UUID,
    background_tasks: BackgroundTasks,
    current_user: Annotated[User, Depends(get_current_user)],
    bookmark_app_service: Annotated[BookmarkAppServices, Depends(BookmarkAppServices)],
):
    """
    Force refetch title extraction from the webpage in the background.
    """
    await bookmark_app_service.refetch_title(current_user, id, background_tasks)
    return ResponseHandler.success(
        message="Title extraction scheduled successfully",
    )
