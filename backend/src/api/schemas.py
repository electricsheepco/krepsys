"""Pydantic schemas for API request/response validation."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, HttpUrl


# ── Feed ─────────────────────────────────────────────────────────────────────

class FeedBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    url: HttpUrl
    fetch_interval: int = Field(default=900, ge=60)


class FeedCreate(FeedBase):
    pass


class FeedUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    is_active: Optional[bool] = None
    fetch_interval: Optional[int] = Field(None, ge=60)


class FeedResponse(FeedBase):
    id: int
    is_active: bool
    last_fetched: Optional[datetime] = None
    created_at: datetime
    model_config = {"from_attributes": True}


# ── Tag ───────────────────────────────────────────────────────────────────────

class TagResponse(BaseModel):
    id: int
    name: str
    model_config = {"from_attributes": True}


# ── Highlight ─────────────────────────────────────────────────────────────────

class HighlightCreate(BaseModel):
    text: str = Field(..., min_length=1)
    color: str = Field(default="yellow", pattern="^(yellow|green|blue|pink)$")
    note: Optional[str] = None


class HighlightUpdate(BaseModel):
    color: Optional[str] = Field(None, pattern="^(yellow|green|blue|pink)$")
    note: Optional[str] = None


class HighlightResponse(BaseModel):
    id: int
    article_id: int
    text: str
    color: str
    note: Optional[str] = None
    created_at: datetime
    model_config = {"from_attributes": True}


# ── Article ───────────────────────────────────────────────────────────────────

class ArticleResponse(BaseModel):
    id: int
    feed_id: int
    title: str
    url: str
    author: Optional[str] = None
    content: Optional[str] = None
    content_text: Optional[str] = None
    note: Optional[str] = None
    published_at: Optional[datetime] = None
    fetched_at: datetime
    is_read: bool
    is_saved: bool
    is_archived: bool
    tags: List[TagResponse] = []
    highlights: List[HighlightResponse] = []
    model_config = {"from_attributes": True}


class ArticleUpdate(BaseModel):
    is_read: Optional[bool] = None
    is_saved: Optional[bool] = None
    is_archived: Optional[bool] = None
    note: Optional[str] = None
