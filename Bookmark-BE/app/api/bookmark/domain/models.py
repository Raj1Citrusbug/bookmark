# Third-party imports
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, Table, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

# Local imports
from app.utils.base_model import ActivityTrackingBaseModel
from app.config.db_connection import Base

# Bridge table for Bookmark <-> Tag many-to-many relationship
bookmark_tags = Table(
    "bookmark_tags",
    Base.metadata,
    Column(
        "bookmark_id",
        UUID(as_uuid=True),
        ForeignKey("bookmarks.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "tag_id",
        UUID(as_uuid=True),
        ForeignKey("tags.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Bookmark(ActivityTrackingBaseModel):
    __tablename__ = "bookmarks"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    url = Column(String, nullable=False)
    title = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    is_archived = Column(Boolean, nullable=False, default=False)
    is_broken = Column(Boolean, nullable=False, default=False)
    broken_reason = Column(String, nullable=True)
    last_checked_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="bookmarks")
    tags = relationship(
        "Tag",
        secondary=bookmark_tags,
        back_populates="bookmarks",
        lazy="selectin",
    )
    broken_link_logs = relationship(
        "BrokenLinkLog",
        back_populates="bookmark",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class BrokenLinkLog(Base):
    __tablename__ = "broken_link_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=func.gen_random_uuid())
    bookmark_id = Column(UUID(as_uuid=True), ForeignKey("bookmarks.id", ondelete="CASCADE"), nullable=False)
    error_message = Column(String, nullable=False)
    checked_at = Column(DateTime(timezone=True), nullable=False, default=func.now())

    # Relationship back to Bookmark
    bookmark = relationship("Bookmark", back_populates="broken_link_logs")