# Third-party imports
from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship

# Local imports
from app.utils.base_model import ActivityTrackingBaseModel


class User(ActivityTrackingBaseModel):
    __tablename__ = "users"

    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String, nullable=False)
    role = Column(String(50), nullable=False, default="USER")
    is_active = Column(Boolean, nullable=False, default=True)

    # Relationships
    bookmarks = relationship(
        "Bookmark",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    tags = relationship(
        "Tag",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )