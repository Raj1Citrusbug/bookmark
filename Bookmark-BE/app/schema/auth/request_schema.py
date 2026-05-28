import re
from pydantic import Field, field_validator, EmailStr
from fastapi import status

from app.schema.base import BaseSchema
from app.utils.custom_exception import CustomException
from app.utils.helpers.common_functions import PASSWORD_REGEX


class SignupUserRequestSchema(BaseSchema):
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=8)

    @field_validator("password")
    @classmethod
    def validate_password_format(cls, value: str) -> str:
        if not re.match(PASSWORD_REGEX, value):
            raise CustomException(
                message="Password must contain at least one uppercase letter, one lowercase letter, one digit, and one special character.",
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            )
        return value


class LoginUserRequestSchema(BaseSchema):
    email: EmailStr
    password: str
    remember_me: bool = False
