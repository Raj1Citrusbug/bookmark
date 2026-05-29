# Standard library imports
from typing import Annotated

# Third-party imports
from fastapi import APIRouter, Depends, status

# Local imports
from app.schema.admin.response_schema import GlobalBrokenLinksResponseSchema
from app.schema.admin.request_schema import AdminBrokenLinksQueryParamsSchema
from app.api.admin.application.services import AdminAppServices
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
    params: AdminBrokenLinksQueryParamsSchema = Depends(),
):
    """
    Retrieve system-wide broken bookmarks dashboard (Admin only).
    """
    result, total_count = await admin_app_service.get_global_broken_links_report(params)
    return ResponseHandler.success_listing(
        message=get_response_message("detail_success", "Global broken links"),
        data=result,
        count=total_count,
    )
