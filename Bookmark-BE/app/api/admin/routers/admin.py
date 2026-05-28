# Standard library imports
from typing import Annotated

# Third-party imports
from fastapi import APIRouter, Depends, status

# Local imports
from app.schema.admin.response_schema import GlobalBrokenLinksResponseSchema
from app.api.admin.application.services import AdminAppServices
from app.api.auth.domain.models import User
from app.utils.response_handler import ResponseHandler
from app.utils.messages.custom_response_messages import get_response_message
from app.utils.middleware.auth_middleware import admin_required

router = APIRouter(prefix="/admin", tags=["Admin Dashboard"])


@router.get(
    "/broken-links",
    status_code=status.HTTP_200_OK,
    response_model=GlobalBrokenLinksResponseSchema,
    dependencies=[Depends(admin_required)],
)
async def get_broken_links(
    admin_app_service: Annotated[AdminAppServices, Depends(AdminAppServices)],
):
    """
    Retrieve system-wide broken bookmarks dashboard (Admin only).
    """
    result = await admin_app_service.get_global_broken_links_report()
    return ResponseHandler.success(
        message=get_response_message("detail_success", "Global broken links"),
        data=result,
    )
