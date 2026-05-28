# Standard library imports
from uuid import uuid4

# Third-party imports
from sqlalchemy import UUID, Column, DateTime, func

# Local imports
from app.config.db_connection import Base


class ActivityTrackingBaseModel(Base):
    """
    Abstract base model for tracking entity activities.
    """

    __abstract__ = True
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.timezone("utc", func.now()),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.timezone("utc", func.now()),
        onupdate=func.timezone("utc", func.now()),
        nullable=False,
    )