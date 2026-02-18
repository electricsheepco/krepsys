"""Pydantic schemas for API request/response validation."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, HttpUrl


class FeedBase(BaseModel):
    """Base schema for feed with common fields."""

    name: str = Field(..., min_length=1, max_length=255, description="Feed name")
    url: HttpUrl = Field(..., description="RSS feed URL")
    fetch_interval: int = Field(default=900, ge=60, description="Fetch interval in seconds (minimum 60)")


class FeedCreate(FeedBase):
    """Schema for creating a new feed."""
    pass


class FeedUpdate(BaseModel):
    """Schema for updating a feed (all fields optional for partial updates)."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    is_active: Optional[bool] = None
    fetch_interval: Optional[int] = Field(None, ge=60)


class FeedResponse(FeedBase):
    """Schema for feed response (includes database fields)."""

    id: int
    is_active: bool
    last_fetched: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ArticleResponse(BaseModel):
    """Schema for article response (includes database fields)."""

    id: int
    feed_id: int
    title: str
    url: str
    author: Optional[str] = None
    content: Optional[str] = None
    content_text: Optional[str] = None
    published_at: Optional[datetime] = None
    fetched_at: datetime
    is_read: bool
    is_saved: bool
    is_archived: bool

    model_config = {"from_attributes": True}


class ArticleUpdate(BaseModel):
    """Schema for updating article status (all fields optional for partial updates)."""

    is_read: Optional[bool] = None
    is_saved: Optional[bool] = None
    is_archived: Optional[bool] = None
