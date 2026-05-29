# Standard library imports
from typing import List, Tuple

# Third-party imports
from fastapi import Depends

# Local imports
from app.api.admin.domain.services import AdminDomainServices
from app.schema.admin.response_schema import GlobalBrokenLinkDataSchema
from app.schema.admin.request_schema import AdminBrokenLinksQueryParamsSchema


class AdminAppServices:
    def __init__(
        self,
        admin_domain_services: AdminDomainServices = Depends(AdminDomainServices),
    ) -> None:
        self.admin_domain_services = admin_domain_services

    async def get_global_broken_links_report(
        self,
        query_params: AdminBrokenLinksQueryParamsSchema,
    ) -> Tuple[List[GlobalBrokenLinkDataSchema], int]:
        """
        Compile system-wide report details of all broken bookmarks (Admin only).
        """
        report_data, total_count = (
            await self.admin_domain_services.get_all_broken_bookmarks(query_params)
        )
        return report_data, total_count
