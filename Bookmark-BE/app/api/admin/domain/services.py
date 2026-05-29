# Standard library imports
from typing import Annotated, List, Tuple

# Third-party imports
from fastapi import Depends
from sqlalchemy import select, Row, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

# Local imports
from app.api.bookmark.domain.models import Bookmark
from app.api.auth.domain.models import User
from app.config.db_connection import get_async_db
from app.schema.admin.request_schema import AdminBrokenLinksQueryParamsSchema
from app.utils.enums import SortOrder


class AdminDomainServices:
    def __init__(
        self, db_session: Annotated[AsyncSession, Depends(get_async_db)]
    ) -> None:
        self.db_session = db_session

    async def get_all_broken_bookmarks(
        self,
        query_params: AdminBrokenLinksQueryParamsSchema,
    ) -> Tuple[List[Row], int]:
        """
        Retrieve specific columns of all broken bookmarks across the entire system
        by joining with the User table, with search and pagination support.
        """
        filters = set()
        filters.add(Bookmark.is_broken == True)

        if query_params.search:
            search_pattern = f"%{query_params.search}%"
            filters.add(
                or_(
                    Bookmark.title.ilike(search_pattern),
                    Bookmark.url.ilike(search_pattern),
                    Bookmark.notes.ilike(search_pattern),
                    User.name.ilike(search_pattern),
                    User.email.ilike(search_pattern),
                )
            )

        query = (
            select(
                Bookmark.id.label("bookmark_id"),
                Bookmark.title.label("bookmark_title"),
                Bookmark.url.label("bookmark_url"),
                User.name.label("owner_name"),
                User.email.label("owner_email"),
                Bookmark.last_checked_at,
                Bookmark.broken_reason,
                func.count().over().label("total_count"),
            )
            .outerjoin(User, Bookmark.user_id == User.id)
            .where(*filters)
        )

        order_by = (
            Bookmark.last_checked_at.asc()
            if query_params.sort_order == SortOrder.ASC
            else Bookmark.last_checked_at.desc()
        )

        # Apply pagination and order
        paginated_query = (
            query.order_by(order_by)
            .offset((query_params.page - 1) * query_params.limit)
            .limit(query_params.limit)
        )
        result = await self.db_session.execute(paginated_query)
        rows = result.all()

        if not rows:
            return [], 0

        total_count = int(rows[0].total_count)
        return list(rows), total_count