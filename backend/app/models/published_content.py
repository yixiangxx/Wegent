from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.sql import func

from app.db.base import Base


class PublishedContent(Base):
    """
    PublishedContent model for storing published videos and images.

    A published content represents a user's decision to showcase their AI-generated
    video or image in the public gallery. It stores metadata like title and description,
    and references the original SubtaskContext (attachment) that contains the actual
    media URLs.
    """

    __tablename__ = "published_contents"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Identification
    user_id = Column(Integer, nullable=False, index=True)  # Publisher
    subtask_id = Column(Integer, nullable=False, index=True)  # Source message
    attachment_id = Column(Integer, nullable=False, index=True)  # SubtaskContext ID
    content_type = Column(String(20), nullable=False)  # "video" or "image"

    # User-provided metadata
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False, default="")
    prompt = Column(Text, nullable=False, default="")  # Original generation prompt

    # Statistics
    view_count = Column(Integer, nullable=False, default=0)
    like_count = Column(Integer, nullable=False, default=0)

    # Status
    is_active = Column(Boolean, nullable=False, default=True)  # For unpublishing
    is_featured = Column(Boolean, nullable=False, default=False)  # Admin feature

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=func.now(), index=True)
    updated_at = Column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )

    # Constraints
    __table_args__ = (
        UniqueConstraint("subtask_id", "attachment_id", name="uniq_subtask_attachment"),
        Index("idx_published_content_type_active", "content_type", "is_active"),
    )
