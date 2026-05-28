from datetime import datetime
from typing import List
from uuid import UUID
from app.schema.base import BaseSchema, BaseResponseSchema


class TagDetailDataSchema(BaseSchema):
    id: UUID
    name: str
    created_at: datetime


class TagCloudDataSchema(BaseSchema):
    name: str
    count: int


class TagCloudResponseSchema(BaseResponseSchema):
    data: List[TagCloudDataSchema]


class TagListResponseSchema(BaseResponseSchema):
    data: List[TagDetailDataSchema]
