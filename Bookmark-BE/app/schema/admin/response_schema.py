from datetime import datetime
from typing import List, Optional
from uuid import UUID
from app.schema.base import BaseSchema, BaseResponseSchema


class GlobalBrokenLinkDataSchema(BaseSchema):
    bookmark_id: UUID
    bookmark_title: Optional[str] = None
    bookmark_url: str
    owner_name: str
    owner_email: str
    last_checked_at: Optional[datetime] = None
    broken_reason: Optional[str] = None


class GlobalBrokenLinksResponseSchema(BaseResponseSchema):
    data: List[GlobalBrokenLinkDataSchema]
