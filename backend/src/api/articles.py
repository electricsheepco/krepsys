"""Article management API endpoints."""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from src.database import get_db
from src.models.article import Article
from src.api.schemas import ArticleResponse, ArticleUpdate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/articles", tags=["articles"])


@router.get("/", response_model=List[ArticleResponse])
def list_articles(
    feed_id: Optional[int] = Query(None, description="Filter by feed ID"),
    is_read: Optional[bool] = Query(None, description="Filter by read status"),
    is_saved: Optional[bool] = Query(None, description="Filter by saved status"),
    is_archived: Optional[bool] = Query(None, description="Filter by archived status"),
    sort: str = Query("newest", pattern="^(newest|oldest)$", description="Sort order: newest or oldest"),
    db: Session = Depends(get_db)
):
    """List articles with optional filtering and sorting.

    Args:
        feed_id: Filter by specific feed
        is_read: Filter by read status (true/false)
        is_saved: Filter by saved status (true/false)
        is_archived: Filter by archived status (true/false)
        sort: Sort order - 'newest' (default) or 'oldest'
        db: Database session

    Returns:
        List of articles matching filters, sorted by requested order
    """
    # Start with base query
    query = db.query(Article)

    # Apply filters dynamically (only if provided)
    if feed_id is not None:
        query = query.filter(Article.feed_id == feed_id)

    if is_read is not None:
        query = query.filter(Article.is_read == is_read)

    if is_saved is not None:
        query = query.filter(Article.is_saved == is_saved)

    if is_archived is not None:
        query = query.filter(Article.is_archived == is_archived)

    # Apply sorting
    if sort == "newest":
        # Sort by published_at descending (newest first), fallback to fetched_at, then ID
        query = query.order_by(
            Article.published_at.desc().nullslast(),
            Article.fetched_at.desc(),
            Article.id.desc()
        )
    else:  # oldest
        # Sort by published_at ascending (oldest first), fallback to fetched_at, then ID
        query = query.order_by(
            Article.published_at.asc().nullsfirst(),
            Article.fetched_at.asc(),
            Article.id.asc()
        )

    articles = query.all()

    return articles


@router.get("/{article_id}", response_model=ArticleResponse)
def get_article(article_id: int, db: Session = Depends(get_db)):
    """Get a specific article by ID.

    Args:
        article_id: Article ID
        db: Database session

    Returns:
        Article with full content

    Raises:
        HTTPException: If article not found
    """
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article with id {article_id} not found"
        )

    return article


@router.patch("/{article_id}", response_model=ArticleResponse)
def update_article(
    article_id: int,
    article_update: ArticleUpdate,
    db: Session = Depends(get_db)
):
    """Update article status (read/saved/archived).

    Args:
        article_id: Article ID
        article_update: Fields to update (partial update)
        db: Database session

    Returns:
        Updated article

    Raises:
        HTTPException: If article not found
    """
    db_article = db.query(Article).filter(Article.id == article_id).first()
    if not db_article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article with id {article_id} not found"
        )

    # Update only provided fields
    update_data = article_update.model_dump(exclude_unset=True)

    # Track changes for logging
    changes = []
    for field, value in update_data.items():
        old_value = getattr(db_article, field)
        if old_value != value:
            changes.append(f"{field}: {old_value} -> {value}")
            setattr(db_article, field, value)

    db.commit()
    db.refresh(db_article)

    # Log status changes
    if changes:
        logger.info(
            f"Updated article: id={db_article.id}, "
            f"title='{db_article.title[:30]}...', "
            f"changes=[{', '.join(changes)}]"
        )

    return db_article
