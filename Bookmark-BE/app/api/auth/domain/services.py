# Standard library imports
from dataclasses import dataclass, asdict
from typing import Annotated
from uuid import UUID

# Third-party imports
from dataclass_type_validator import dataclass_validate
from fastapi import Depends, status
from sqlalchemy import exc, select
from sqlalchemy.ext.asyncio import AsyncSession

# Local application imports
from app.api.auth.domain.models import User
from app.config.db_connection import get_async_db
from app.utils.custom_exception import CustomException
from app.utils.helpers.common_functions import extract_message_from_integrity_error
from app.config.logger import logger


@dataclass_validate(before_post_init=True)
@dataclass(frozen=True)
class UserDataClass:
    name: str
    email: str
    password_hash: str
    role: str
    is_active: bool = True


class UserFactory:
    @staticmethod
    def build_entity(user_data: UserDataClass) -> User:
        """Build and return a User entity."""
        user_dict = asdict(user_data)
        return User(**user_dict)


class UserDomainServices:
    def __init__(
        self, db_session: Annotated[AsyncSession, Depends(get_async_db)]
    ) -> None:
        """Initialize the UserDomainServices class."""
        self.db_session = db_session

    def get_factory(self) -> type[UserFactory]:
        """Return the UserFactory class."""
        return UserFactory

    async def create_user(self, user_data: UserDataClass) -> User:
        """Create a new user."""
        try:
            user = self.get_factory().build_entity(user_data)
            self.db_session.add(user)
            await self.db_session.commit()
            await self.db_session.refresh(user)
            return user
        except exc.IntegrityError as ie:
            await self.db_session.rollback()
            logger.error("Integrity Error while creating user: %s", ie)
            message = extract_message_from_integrity_error(str(ie.orig))
            raise CustomException(
                message=message,
                status_code=status.HTTP_409_CONFLICT,
            )
        except exc.SQLAlchemyError as sqe:
            await self.db_session.rollback()
            logger.error("SQLAlchemy Error while creating user: %s", sqe)
            raise sqe
        except Exception as e:
            await self.db_session.rollback()
            logger.error("General Exception while creating user: %s", e)
            raise e

    async def get_user_by_email(self, email: str) -> User | None:
        """Fetch a user by their email address."""
        query = select(User).where(User.email == email)
        result = await self.db_session.execute(query)
        return result.scalars().first()

    async def get_user_by_id(self, user_id: UUID) -> User | None:
        """Fetch a user by their ID."""
        query = select(User).where(User.id == user_id)
        result = await self.db_session.execute(query)
        return result.scalars().first()
