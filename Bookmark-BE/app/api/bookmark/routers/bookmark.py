# Standard library imports
from typing import Annotated
from uuid import UUID

# Third-party imports
from fastapi import APIRouter, Depends, status

# Local imports
from app.schema.bookmark.request_schema import (
    BookmarkCreateRequestSchema,
    BookmarkUpdateRequestSchema,
    BookmarkQueryParamsSchema,
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
    current_user: Annotated[User, Depends(get_current_user)],
    bookmark_app_service: Annotated[BookmarkAppServices, Depends(BookmarkAppServices)],
) -> BaseResponseSchema:
    """
    Save a new bookmark. If the title is omitted, it will be automatically fetched in the background.
    """
    result = await bookmark_app_service.create_bookmark(
        current_user, bookmark_data
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
    params: BookmarkQueryParamsSchema = Depends(),
) -> BookmarkListResponseSchema:
    """
    Browse user's saved bookmarks with search and tag filters.
    """
    result, total_count = await bookmark_app_service.get_bookmarks(
        current_user,
        params,
    )
    return ResponseHandler.success_listing(
        message=get_response_message("detail_success", "Bookmarks"),
        data=result,
        count=total_count,
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
    response_model=BaseResponseSchema,
)
async def archive_bookmark(
    id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    bookmark_app_service: Annotated[BookmarkAppServices, Depends(BookmarkAppServices)],
) -> BaseResponseSchema:
    """
    Toggle the archive status of a bookmark.
    """
    await bookmark_app_service.archive_bookmark(current_user, id)
    return ResponseHandler.success(
        message=get_response_message("update_success", "Bookmark archived status"),
    )


@router.post(
    "/{id}/refetch-title",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=BaseResponseSchema,
)
async def refetch_title(
    id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    bookmark_app_service: Annotated[BookmarkAppServices, Depends(BookmarkAppServices)],
):
    """
    Force refetch title extraction from the webpage in the background.
    """
    await bookmark_app_service.refetch_title(current_user, id)
    return ResponseHandler.success(
        message="Title extraction scheduled successfully",
    )
