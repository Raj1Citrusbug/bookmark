from pydantic import Field, ConfigDict
from app.schema.base import BaseSchema


class TagCreateRequestSchema(BaseSchema):
    name: str = Field(..., min_length=1, max_length=100)

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "name": "work",
            }
        },
    )
