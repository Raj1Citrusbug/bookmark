# Standard library imports
from typing import Annotated

# Third-party imports
from fastapi import APIRouter, Depends, status

# Local imports
from app.schema.auth.request_schema import SignupUserRequestSchema, LoginUserRequestSchema
from app.schema.auth.response_schema import LoginResponseSchema, UserResponseSchema
from app.schema.base import BaseResponseSchema
from app.api.auth.application.services import UserAppServices
from app.api.auth.domain.models import User
from app.utils.response_handler import ResponseHandler
from app.utils.messages.custom_response_messages import get_response_message
from app.utils.middleware.auth_middleware import get_current_user

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])
user_router = APIRouter(prefix="/users", tags=["Users"])


@auth_router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=BaseResponseSchema,
)
async def register(
    user_data: SignupUserRequestSchema,
    user_app_service: Annotated[UserAppServices, Depends(UserAppServices)],
):
    """
    Register a new user account.
    """
    await user_app_service.register_user(user_data)
    return ResponseHandler.success(
        message=get_response_message("signup_success"),
    )


@auth_router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=LoginResponseSchema,
)
async def login(
    user_data: LoginUserRequestSchema,
    user_app_service: Annotated[UserAppServices, Depends(UserAppServices)],
):
    """
    Authenticate user and return access token.
    """
    result = await user_app_service.login_user(user_data)
    return ResponseHandler.success(
        message=get_response_message("login_success"),
        data=result,
    )


@user_router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponseSchema,
)
async def get_me(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Retrieve profile details of the currently authenticated user.
    """
    user_data = UserResponseSchema(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        role=current_user.role,
        is_active=current_user.is_active,
    )
    return ResponseHandler.success(
        message=get_response_message("detail_success", "User profile"),
        data=user_data.model_dump(),
    )
