# Standard library imports
import re
from uuid import UUID

# Third-party imports
from typing import List, Optional
from fastapi import status
from pydantic import Field, field_validator, ConfigDict

# Local application imports
from app.schema.base import BaseSchema

from app.utils.custom_exception import CustomException
from app.utils.helpers.common_functions import URL_REGEX


class BookmarkCreateRequestSchema(BaseSchema):
    url: str
    title: Optional[str] = Field(default=None)
    notes: Optional[str] = Field(default=None)
    tags: Optional[List[UUID]] = Field(default=[])

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "url": "https://example.com",
                "title": "Example Domain",
                "notes": "A useful website for testing.",
                "tags": [
                    "123e4567-e89b-12d3-a456-426614174000",
                    "123e4567-e89b-12d3-a456-426614174001",
                ],
            }
        },
    )

    @field_validator("url")
    @classmethod
    def validate_url(cls, value: str) -> str:
        if not re.match(URL_REGEX, value):
            raise CustomException(
                message="Please enter a valid URL.",
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            )
        return value


class BookmarkUpdateRequestSchema(BaseSchema):
    title: Optional[str] = Field(default=None)
    notes: Optional[str] = Field(default=None)
    tags: Optional[List[UUID]] = Field(default=None)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Updated Title",
                "notes": "Updated notes for this bookmark.",
                "tags": ["123e4567-e89b-12d3-a456-426614174000"],
            }
        },
    )
