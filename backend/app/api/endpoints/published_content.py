from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core import security
from app.models.user import User
from app.schemas.published_content import (
    PublishedContentCreate,
    PublishedContentListResponse,
    PublishedContentResponse,
)
from app.services.published_content_service import PublishedContentService

router = APIRouter()


@router.post("", response_model=PublishedContentResponse)
def publish_content(
    data: PublishedContentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user),
):
    """
    Publish a video or image to the public gallery.

    Requires authentication. Validates ownership of the content before publishing.
    """
    return PublishedContentService.create_published_content(
        db=db, user_id=current_user.id, data=data
    )


@router.get("", response_model=PublishedContentListResponse)
def list_published_contents(
    content_type: Optional[str] = Query(
        None, description="Filter by content type: video or image"
    ),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
):
    """
    List published contents (public endpoint, no auth required).

    Returns paginated list ordered by featured status and creation time.
    """
    return PublishedContentService.list_published_contents(
        db=db, content_type=content_type, page=page, page_size=page_size
    )


@router.get(
    "/check/{subtask_id}", response_model=Optional[PublishedContentResponse]
)
def check_published_status(
    subtask_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user),
):
    """
    Check if a content is already published.

    Requires authentication. Returns the published record if exists, otherwise returns null.
    """
    return PublishedContentService.check_if_published(
        db=db,
        user_id=current_user.id,
        subtask_id=subtask_id,
    )
