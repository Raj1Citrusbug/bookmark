# Third-party imports
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

# Local imports
from app.utils.base_model import ActivityTrackingBaseModel
from app.api.bookmark.domain.models import bookmark_tags


class Tag(ActivityTrackingBaseModel):
    __tablename__ = "tags"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)

    # Relationships
    user = relationship("User", back_populates="tags")
    bookmarks = relationship(
        "Bookmark",
        secondary=bookmark_tags,
        back_populates="tags",
        lazy="selectin",
    )
