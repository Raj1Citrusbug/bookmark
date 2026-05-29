# Third-party imports
from fastapi import Depends, status
from passlib.context import CryptContext

# Local application imports
from app.api.auth.domain.services import UserDomainServices, UserDataClass
from app.schema.auth.request_schema import (
    SignupUserRequestSchema,
    LoginUserRequestSchema,
)
from app.schema.auth.response_schema import LoginDataResponseSchema
from app.utils.custom_exception import CustomException
from app.utils.enums import RoleType
from app.utils.messages.custom_response_messages import get_response_message
from app.utils.service.token_service import TokenServices, AccessTokenData

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
token_services = TokenServices()


class UserAppServices:
    def __init__(
        self,
        user_domain_services: UserDomainServices = Depends(UserDomainServices),
    ) -> None:
        self.user_domain_services = user_domain_services

    def hash_password(self, password: str) -> str:
        """
        Hash the plain text password using bcrypt.
        """
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify the plain text password against the hashed password.
        """
        return pwd_context.verify(plain_password, hashed_password)

    async def register_user(self, signup_data: SignupUserRequestSchema) -> None:
        """
        Handle registration of a new user.
        """
        # Check if user already exists
        existing_user = await self.user_domain_services.get_user_by_email(
            signup_data.email.lower()
        )
        if existing_user:
            raise CustomException(
                message=get_response_message("user_already_exists", "email"),
                status_code=status.HTTP_409_CONFLICT,
            )

        # Hash password and create user
        password_hash = self.hash_password(signup_data.password)
        user_data = UserDataClass(
            name=signup_data.name,
            email=signup_data.email.lower(),
            password_hash=password_hash,
            role=RoleType.USER.value,  # Default role is USER
            is_active=True,
        )

        user = await self.user_domain_services.create_user(user_data)

        return None

    async def login_user(self, login_data: LoginUserRequestSchema) -> dict:
        """
        Authenticate a user and generate access and refresh tokens.
        """
        user = await self.user_domain_services.get_user_by_email(
            login_data.email.lower()
        )
        if not user or not self.verify_password(
            login_data.password, user.password_hash
        ):
            raise CustomException(
                message=get_response_message("invalid_credentials"),
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if not user.is_active:
            raise CustomException(
                message=get_response_message("user_not_active"),
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # Generate tokens
        token_data = AccessTokenData(
            user_id=str(user.id),
            name=user.name,
            email=user.email,
            role=user.role,
            remember_me=login_data.remember_me,
        )
        access_token = token_services.generate_access_token(token_data)

        return LoginDataResponseSchema(
            access_token=access_token,
            user=user,
        )
