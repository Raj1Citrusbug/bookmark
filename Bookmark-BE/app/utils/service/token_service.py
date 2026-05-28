import jwt
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from fastapi import status

from app.config.settings import app_settings
from app.utils.custom_exception import CustomException
from app.utils.enums import TokenType
from app.utils.messages.custom_response_messages import get_response_message


@dataclass
class AccessTokenData:
    user_id: str
    name: str
    email: str
    role: str
    remember_me: bool = False


class TokenServices:
    """
    Service class for handling JWT token operations.
    """

    def __init__(self):
        self.secret_key = app_settings.JWT_SECRET_KEY
        self.algorithm = app_settings.JWT_ALGORITHM
        self.access_token_lifetime = app_settings.JWT_ACCESS_TOKEN_LIFETIME
        self.remember_me_lifetime = app_settings.JWT_REMEMBER_ME_LIFETIME
        self.verification_token_lifetime = app_settings.JWT_VERIFICATION_TOKEN_LIFETIME
        self.forgot_password_token_lifetime = (
            app_settings.JWT_FORGOT_PASSWORD_TOKEN_LIFETIME
        )

    def _get_expiration_time(self, lifetime_str: str) -> datetime:
        days, hours, minutes, seconds = map(int, lifetime_str.split(","))
        return datetime.now(UTC) + timedelta(
            days=days, hours=hours, minutes=minutes, seconds=seconds
        )

    def generate_access_token(self, data: AccessTokenData) -> str:
        try:
            expiration = self._get_expiration_time(
                self.access_token_lifetime
                if not data.remember_me
                else self.remember_me_lifetime
            )
            payload = {
                "user_id": data.user_id,
                "name": data.name,
                "email": data.email,
                "role": data.role,
                "exp": expiration,
                "iat": datetime.now(UTC),
                "type": "access",
            }
            return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        except Exception:
            raise CustomException(
                message=get_response_message("token_generation_failed", "access"),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def generate_verification_token(
        self, user_id: str, token_type: str = "verification"
    ) -> str:
        try:
            if token_type == TokenType.RESET_TOKEN.value:
                expiry = self._get_expiration_time(self.forgot_password_token_lifetime)
            else:
                expiry = self._get_expiration_time(self.verification_token_lifetime)

            payload = {
                "user_id": str(user_id),
                "exp": expiry,
                "type": token_type,
                "iat": datetime.now(UTC),
            }
            return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        except Exception:
            raise CustomException(
                message=get_response_message("token_generation_failed", "verification"),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def verify_token(self, token: str, expected_type: str | None = None) -> dict:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            actual_type = payload.get("type")

            if expected_type and actual_type != expected_type:
                raise CustomException(
                    message=f"Invalid token type: expected {expected_type}, got {actual_type}",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            return payload
        except jwt.ExpiredSignatureError:
            raise CustomException(
                message=get_response_message("token_expired"),
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        except jwt.InvalidTokenError:
            raise CustomException(
                message=get_response_message("invalid_token"),
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        except Exception as e:
            raise CustomException(
                message=f"Token verification failed: {str(e)}",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
