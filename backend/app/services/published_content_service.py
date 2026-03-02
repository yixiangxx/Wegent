from typing import Optional

from fastapi import HTTPException
from sqlalchemy import and_, desc, func
from sqlalchemy.orm import Session

from app.models.published_content import PublishedContent
from app.models.subtask import Subtask
from app.models.subtask_context import SubtaskContext
from app.models.user import User
from app.schemas.published_content import (
    PublishedContentCreate,
    PublishedContentListResponse,
    PublishedContentResponse,
    PublishedContentUpdate,
)


class PublishedContentService:
    """Service layer for published content operations."""

    @staticmethod
    def create_published_content(
        db: Session, user_id: int, data: PublishedContentCreate
    ) -> PublishedContentResponse:
        """
        Create a new published content.

        Validates:
        1. Subtask exists and belongs to user's task
        2. Finds attachment from SubtaskContext based on content_type
        3. Extracts prompt from previous user subtask in the same task
        4. No duplicate publish (UniqueConstraint on subtask_id + attachment_id)
        """
        # Fetch the subtask
        subtask = db.query(Subtask).filter(Subtask.id == data.subtask_id).first()

        if not subtask:
            raise HTTPException(status_code=404, detail="Subtask not found")

        # Verify subtask belongs to user's task
        from app.models.task import TaskResource

        task = db.query(TaskResource).filter(TaskResource.id == subtask.task_id).first()

        if not task or task.user_id != user_id:
            raise HTTPException(
                status_code=403, detail="Not authorized to publish this content"
            )

        # Find attachment from SubtaskContext based on content_type
        attachment = (
            db.query(SubtaskContext)
            .filter(
                SubtaskContext.subtask_id == data.subtask_id,
                SubtaskContext.context_type == "attachment",
            )
            .first()
        )

        if not attachment:
            raise HTTPException(
                status_code=404, detail="No attachment found for this subtask"
            )

        # Validate content_type matches attachment metadata
        type_data = attachment.type_data or {}
        if data.content_type == "video":
            if "video_metadata" not in type_data:
                raise HTTPException(
                    status_code=400, detail="Attachment does not contain video metadata"
                )
        elif data.content_type == "image":
            if "image_metadata" not in type_data:
                raise HTTPException(
                    status_code=400, detail="Attachment does not contain image metadata"
                )
        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid content_type, must be 'video' or 'image'",
            )

        # Extract prompt from previous user subtask
        prompt = ""
        previous_user_subtask = (
            db.query(Subtask)
            .filter(
                Subtask.task_id == subtask.task_id,
                Subtask.id < data.subtask_id,
                Subtask.role == "user",
            )
            .order_by(desc(Subtask.id))
            .first()
        )

        if previous_user_subtask:
            prompt = previous_user_subtask.prompt or ""

        # Check for duplicate (UniqueConstraint will catch this, but we can provide better error)
        existing = (
            db.query(PublishedContent)
            .filter(
                and_(
                    PublishedContent.subtask_id == data.subtask_id,
                    PublishedContent.attachment_id == attachment.id,
                )
            )
            .first()
        )

        if existing:
            raise HTTPException(status_code=409, detail="Content already published")

        # Create published content
        published_content = PublishedContent(
            user_id=user_id,
            subtask_id=data.subtask_id,
            attachment_id=attachment.id,
            content_type=data.content_type,
            title=data.title,
            description=data.description or "",
            prompt=prompt,
        )

        db.add(published_content)
        db.commit()
        db.refresh(published_content)

        # Return enriched response
        return PublishedContentService._enrich_response(db, published_content)

    @staticmethod
    def list_published_contents(
        db: Session,
        content_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PublishedContentListResponse:
        """
        List published contents with pagination and filtering.

        Order by: is_featured DESC, created_at DESC
        """
        query = db.query(PublishedContent).filter(PublishedContent.is_active == True)

        # Filter by content_type
        if content_type:
            query = query.filter(PublishedContent.content_type == content_type)

        # Get total count
        total = query.count()

        # Apply ordering and pagination
        items = (
            query.order_by(desc(PublishedContent.is_featured), desc(PublishedContent.created_at))
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        # Enrich each item
        enriched_items = [
            PublishedContentService._enrich_response(db, item) for item in items
        ]

        return PublishedContentListResponse(
            items=enriched_items, total=total, page=page, page_size=page_size
        )

    @staticmethod
    def check_if_published(
        db: Session, user_id: int, subtask_id: int
    ) -> Optional[PublishedContentResponse]:
        """
        Check if a content is already published.

        Returns the published content if exists, None otherwise.
        """
        # Verify ownership first
        subtask = db.query(Subtask).filter(Subtask.id == subtask_id).first()

        if not subtask:
            raise HTTPException(status_code=404, detail="Subtask not found")

        from app.models.task import TaskResource

        task = db.query(TaskResource).filter(TaskResource.id == subtask.task_id).first()

        if not task or task.user_id != user_id:
            raise HTTPException(
                status_code=403, detail="Not authorized to access this content"
            )

        # Find published content by subtask_id
        published = (
            db.query(PublishedContent)
            .filter(PublishedContent.subtask_id == subtask_id)
            .first()
        )

        if not published:
            return None

        return PublishedContentService._enrich_response(db, published)

    @staticmethod
    def _enrich_response(
        db: Session, published_content: PublishedContent
    ) -> PublishedContentResponse:
        """
        Enrich published content with user info and media URLs from SubtaskContext.
        """
        # Fetch user info
        user = db.query(User).filter(User.id == published_content.user_id).first()
        username = user.user_name if user else None

        # Fetch attachment to get URLs
        attachment = (
            db.query(SubtaskContext)
            .filter(SubtaskContext.id == published_content.attachment_id)
            .first()
        )

        type_data = attachment.type_data or {} if attachment else {}

        # Extract media URLs based on content_type
        video_url = None
        video_thumbnail = None
        video_duration = None
        image_urls = None

        if published_content.content_type == "video":
            video_metadata = type_data.get("video_metadata", {})
            video_url = video_metadata.get("video_url")
            video_thumbnail = video_metadata.get("thumbnail")
            video_duration = video_metadata.get("duration")
        elif published_content.content_type == "image":
            image_metadata = type_data.get("image_metadata", {})
            image_urls = image_metadata.get("image_urls", [])

        return PublishedContentResponse(
            id=published_content.id,
            user_id=published_content.user_id,
            subtask_id=published_content.subtask_id,
            attachment_id=published_content.attachment_id,
            content_type=published_content.content_type,
            title=published_content.title,
            description=published_content.description,
            prompt=published_content.prompt,
            view_count=published_content.view_count,
            like_count=published_content.like_count,
            is_active=published_content.is_active,
            is_featured=published_content.is_featured,
            created_at=published_content.created_at,
            updated_at=published_content.updated_at,
            username=username,
            avatar=None,
            video_url=video_url,
            video_thumbnail=video_thumbnail,
            video_duration=video_duration,
            image_urls=image_urls,
        )
