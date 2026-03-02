from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class PublishedContentCreate(BaseModel):
    """Schema for creating a published content."""

    subtask_id: int = Field(..., description="ID of the subtask containing the generated content")
    content_type: str = Field(..., description="Type of content: video or image")
    title: str = Field(..., max_length=200, description="Title of the published work")
    description: Optional[str] = Field(
        None, max_length=2000, description="Description of the published work"
    )


class PublishedContentUpdate(BaseModel):
    """Schema for updating a published content."""

    title: Optional[str] = Field(None, max_length=200, description="New title")
    description: Optional[str] = Field(
        None, max_length=2000, description="New description"
    )


class PublishedContentResponse(BaseModel):
    """Schema for published content response with enriched data."""

    id: int
    user_id: int
    subtask_id: int
    attachment_id: int
    content_type: str
    title: str
    description: Optional[str] = None
    prompt: Optional[str] = None
    view_count: int
    like_count: int
    is_active: bool
    is_featured: bool
    created_at: datetime
    updated_at: datetime

    # Enriched data
    username: Optional[str] = Field(
        None, description="Username of the publisher (from User table)"
    )
    avatar: Optional[str] = Field(
        None, description="Avatar URL of the publisher (from User table)"
    )
    video_url: Optional[str] = Field(
        None, description="Video URL (from SubtaskContext.type_data)"
    )
    video_thumbnail: Optional[str] = Field(
        None, description="Video thumbnail URL (from SubtaskContext.type_data)"
    )
    video_duration: Optional[float] = Field(
        None, description="Video duration in seconds (from SubtaskContext.type_data)"
    )
    image_urls: Optional[List[str]] = Field(
        None, description="Image URLs (from SubtaskContext.type_data)"
    )

    class Config:
        from_attributes = True


class PublishedContentListResponse(BaseModel):
    """Schema for paginated published content list."""

    items: List[PublishedContentResponse]
    total: int
    page: int
    page_size: int
