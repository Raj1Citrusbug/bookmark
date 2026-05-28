# Standard library imports
from typing import List

# Third-party imports
from fastapi import Depends

# Local imports
from app.api.admin.domain.services import AdminDomainServices
from app.schema.admin.response_schema import GlobalBrokenLinkDataSchema


class AdminAppServices:
    def __init__(
        self,
        admin_domain_services: AdminDomainServices = Depends(AdminDomainServices),
    ) -> None:
        self.admin_domain_services = admin_domain_services

    async def get_global_broken_links_report(self) -> List[GlobalBrokenLinkDataSchema]:
        """
        Compile system-wide report details of all broken bookmarks (Admin only).
        """
        bookmarks = await self.admin_domain_services.get_all_broken_bookmarks()
        return [
            GlobalBrokenLinkDataSchema(
                bookmark_id=b.id,
                bookmark_title=b.title,
                bookmark_url=b.url,
                owner_name=b.user.name if b.user else "Unknown",
                owner_email=b.user.email if b.user else "Unknown",
                last_checked_at=b.last_checked_at,
                broken_reason=b.broken_reason,
            )
            for b in bookmarks
        ]
