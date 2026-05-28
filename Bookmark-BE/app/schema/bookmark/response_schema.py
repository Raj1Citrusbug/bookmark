from datetime import datetime
from typing import List, Optional
from uuid import UUID
from app.schema.base import BaseSchema, BaseResponseSchema, BaseListingResponseSchema


class TagResponseSchema(BaseSchema):
    id: UUID
    name: str


class BookmarkDetailDataSchema(BaseSchema):
    id: UUID
    user_id: UUID
    url: str
    title: Optional[str] = None
    notes: Optional[str] = None
    is_archived: bool
    is_broken: bool
    broken_reason: Optional[str] = None
    last_checked_at: Optional[datetime] = None
    tags: List[TagResponseSchema]
    created_at: datetime
    updated_at: datetime


class BookmarkResponseSchema(BaseResponseSchema):
    data: BookmarkDetailDataSchema


class BookmarkListResponseSchema(BaseListingResponseSchema):
    data: List[BookmarkDetailDataSchema]
