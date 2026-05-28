# Standard library imports
from typing import Annotated

# Third-party imports
from fastapi import APIRouter, Depends, status

# Local imports
from app.schema.base import BaseResponseSchema
from app.schema.tag.request_schema import TagCreateRequestSchema
from app.schema.tag.response_schema import TagListResponseSchema, TagCloudResponseSchema
from app.api.tag.application.services import TagAppServices
from app.api.auth.domain.models import User
from app.utils.response_handler import ResponseHandler
from app.utils.messages.custom_response_messages import get_response_message
from app.utils.middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/tags", tags=["Tags"])


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=TagListResponseSchema,
)
async def get_tags(
    current_user: Annotated[User, Depends(get_current_user)],
    tag_app_service: Annotated[TagAppServices, Depends(TagAppServices)],
):
    """
    Get all tags created by the authenticated user.
    """
    result = await tag_app_service.get_tags_by_user(current_user)
    return ResponseHandler.success(
        message=get_response_message("detail_success", "Tags"),
        data=result,
    )


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=BaseResponseSchema,
)
async def create_tag(
    tag_data: TagCreateRequestSchema,
    current_user: Annotated[User, Depends(get_current_user)],
    tag_app_service: Annotated[TagAppServices, Depends(TagAppServices)],
):
    """
    Create a new custom tag.
    """
    await tag_app_service.create_tag(current_user, tag_data)
    return ResponseHandler.success(
        message=get_response_message("create_success", "Tag"),
    )


@router.get(
    "/cloud",
    status_code=status.HTTP_200_OK,
    response_model=TagCloudResponseSchema,
)
async def get_tag_cloud(
    current_user: Annotated[User, Depends(get_current_user)],
    tag_app_service: Annotated[TagAppServices, Depends(TagAppServices)],
):
    """
    Get tag cloud data (tag names with bookmark counts).
    """
    result = await tag_app_service.get_tag_cloud(current_user)
    return ResponseHandler.success(
        message=get_response_message("detail_success", "Tag cloud"),
        data=result,
    )
