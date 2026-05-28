# Standard library imports
from typing import Annotated

# Third-party imports
from fastapi import Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

# Local imports
from app.api.auth.domain.models import User
from app.api.auth.domain.services import UserDomainServices
from app.config.db_connection import get_async_db
from app.utils.custom_exception import CustomException
from app.utils.enums import RoleType
from app.utils.messages.custom_response_messages import get_response_message
from app.utils.service.token_service import TokenServices

token_services = TokenServices()
security_bearer_schema = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_bearer_schema),
    db_session: Session = Depends(get_async_db),
) -> User:
    """
    Get current authenticated user from token.
    """
    payload = token_services.verify_token(token=credentials.credentials)
    user_id = payload.get("user_id")

    user_domain_services = UserDomainServices(db_session=db_session)
    user = await user_domain_services.get_user_by_id(user_id)

    if not user:
        raise CustomException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message=get_response_message("user_not_found"),
        )

    if not user.is_active:
        raise CustomException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message=get_response_message("user_not_active"),
        )

    return user


async def admin_required(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency to restrict access to admin users only.
    """
    if current_user.role != RoleType.ADMIN.value:
        raise CustomException(
            message=get_response_message("permission_denied"),
            status_code=status.HTTP_403_FORBIDDEN,
        )
    return current_user
