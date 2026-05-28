from uuid import UUID
from app.schema.base import BaseSchema, BaseResponseSchema


class UserResponseSchema(BaseSchema):
    id: UUID
    name: str
    email: str
    role: str
    is_active: bool


class UserProfileResponseSchema(BaseResponseSchema):
    data: UserResponseSchema

class LoginDataResponseSchema(BaseSchema):
    access_token: str
    user: UserResponseSchema


class LoginResponseSchema(BaseResponseSchema):
    data: LoginDataResponseSchema
