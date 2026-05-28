# Standard library imports
import re

# Third-party imports
from typing import List, Optional
from fastapi import status
from pydantic import Field, field_validator

# Local application imports
from app.schema.base import BaseSchema

from app.utils.custom_exception import CustomException
from app.utils.helpers.common_functions import URL_REGEX


class BookmarkCreateRequestSchema(BaseSchema):
    url: str
    title: Optional[str] = Field(default=None)
    notes: Optional[str] = Field(default=None)
    tags: Optional[List[str]] = Field(default=[])

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
    url: Optional[str] = Field(default=None)
    title: Optional[str] = Field(default=None)
    notes: Optional[str] = Field(default=None)
    tags: Optional[List[str]] = Field(default=None)

    @field_validator("url")
    @classmethod
    def validate_url(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and not re.match(URL_REGEX, value):
            raise CustomException(
                message="Please enter a valid URL.",
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            )
        return value
