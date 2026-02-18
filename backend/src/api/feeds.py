"""Feed management API endpoints."""

import logging
from typing import List
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.database import get_db
from src.models.feed import Feed
from src.api.schemas import FeedCreate, FeedUpdate, FeedResponse
from src.utils.fetcher import fetch_feed

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/feeds", tags=["feeds"])


@router.get("/", response_model=List[FeedResponse])
def list_feeds(db: Session = Depends(get_db)):
    """List all feeds.
    
    Args:
        db: Database session
        
    Returns:
        List of all feeds
    """
    feeds = db.query(Feed).all()
    return feeds


@router.post("/", response_model=FeedResponse, status_code=status.HTTP_201_CREATED)
def create_feed(feed: FeedCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Create a new feed.
    
    Args:
        feed: Feed creation data
        db: Database session
        
    Returns:
        Created feed
        
    Raises:
        HTTPException: If feed URL already exists
    """
    # Check for duplicate URL
    existing_feed = db.query(Feed).filter(Feed.url == str(feed.url)).first()
    if existing_feed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Feed with URL {feed.url} already exists"
        )
    
    # Create new feed
    db_feed = Feed(
        name=feed.name,
        url=str(feed.url),
        fetch_interval=feed.fetch_interval
    )
    db.add(db_feed)
    db.commit()
    db.refresh(db_feed)
    
    logger.info(f"Created feed: id={db_feed.id}, name='{db_feed.name}', url='{db_feed.url}'")
    background_tasks.add_task(fetch_feed, db_feed.id, db_feed.url, db)

    return db_feed


@router.get("/{feed_id}", response_model=FeedResponse)
def get_feed(feed_id: int, db: Session = Depends(get_db)):
    """Get a specific feed by ID.
    
    Args:
        feed_id: Feed ID
        db: Database session
        
    Returns:
        Feed with specified ID
        
    Raises:
        HTTPException: If feed not found
    """
    feed = db.query(Feed).filter(Feed.id == feed_id).first()
    if not feed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feed with id {feed_id} not found"
        )
    return feed


@router.post("/{feed_id}/refresh", status_code=status.HTTP_200_OK)
def refresh_feed(feed_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Trigger a manual fetch for a feed."""
    feed = db.query(Feed).filter(Feed.id == feed_id).first()
    if not feed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Feed {feed_id} not found")
    background_tasks.add_task(fetch_feed, feed.id, feed.url, db)
    return {"status": "fetch scheduled"}


@router.patch("/{feed_id}", response_model=FeedResponse)
def update_feed(feed_id: int, feed_update: FeedUpdate, db: Session = Depends(get_db)):
    """Update a feed (partial update).
    
    Args:
        feed_id: Feed ID
        feed_update: Fields to update
        db: Database session
        
    Returns:
        Updated feed
        
    Raises:
        HTTPException: If feed not found
    """
    db_feed = db.query(Feed).filter(Feed.id == feed_id).first()
    if not db_feed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feed with id {feed_id} not found"
        )
    
    # Update only provided fields
    update_data = feed_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_feed, field, value)
    
    db.commit()
    db.refresh(db_feed)
    
    logger.info(f"Updated feed: id={db_feed.id}, fields={list(update_data.keys())}")
    
    return db_feed


@router.delete("/{feed_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_feed(feed_id: int, db: Session = Depends(get_db)):
    """Delete a feed.
    
    Args:
        feed_id: Feed ID
        db: Database session
        
    Raises:
        HTTPException: If feed not found
    """
    db_feed = db.query(Feed).filter(Feed.id == feed_id).first()
    if not db_feed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feed with id {feed_id} not found"
        )
    
    logger.info(f"Deleting feed: id={db_feed.id}, name='{db_feed.name}'")
    
    db.delete(db_feed)
    db.commit()
    
    return None
