from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.utils.enums import SortOrder


class BaseSchema(BaseModel):
    """Base schema class."""

    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
        str_strip_whitespace=True,
    )


class BaseResponseSchema(BaseSchema):
    """Base response schema."""

    success: bool = True
    message: str
    data: list | dict | bool | str | None = None


class BaseListingResponseSchema(BaseResponseSchema):
    """Base response schema for listings."""

    count: int


class BaseQueryParams(BaseModel):
    """Base query parameters."""

    search: Optional[str] = Field(
        default=None, description="Search term to filter the data"
    )
    page: int = Field(default=1, ge=1, description="Page number (starts from 1)")
    limit: int = Field(
        default=10, le=100, ge=1, description="Number of records per page (max 100)"
    )
    sort_order: Optional[SortOrder] = Field(
        default=SortOrder.DESC.value,
        description="Sort order: 'asc' or 'desc', default is 'desc'",
    )

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if hasattr(cls, "SEARCH_FIELDS"):
            search_fields = getattr(cls, "SEARCH_FIELDS")
            if search_fields:
                if len(search_fields) > 1:
                    formatted_fields = (
                        ", ".join(search_fields[:-1]) + f" or {search_fields[-1]}"
                    )
                else:
                    formatted_fields = search_fields[0]

                cls.model_fields["search"].description = (
                    f"Search term to filter by {formatted_fields}"
                )

    def __init_subclass__(cls, **kwargs):
        """

        Initialize subclass with search fields.



        This method is called when the BaseQueryParams class is subclassed.

        It sets the description of the search field to include the fields that can be searched.

        """

        super().__init_subclass__(**kwargs)
        if hasattr(cls, "SEARCH_FIELDS"):
            search_fields = getattr(cls, "SEARCH_FIELDS")
            if search_fields:
                if len(search_fields) > 1:
                    formatted_fields = (
                        ", ".join(search_fields[:-1]) + f" or {search_fields[-1]}"
                    )
                else:
                    formatted_fields = search_fields[0]
                cls.model_fields["search"].description = (
                    f"Search term to filter by {formatted_fields}"
                )
