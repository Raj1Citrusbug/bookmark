from typing import ClassVar
from pydantic import Field
from app.schema.base import BaseQueryParams


class AdminBrokenLinksQueryParamsSchema(BaseQueryParams):
    """Query parameters for admin broken links endpoint."""

    SEARCH_FIELDS: ClassVar[list[str]] = ["title", "notes", "url", "owner_name", "owner_email"]
