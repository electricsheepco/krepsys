"""Article model for storing fetched articles."""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.database import Base
from src.models.tag import article_tags


class Article(Base):
    """Article model."""

    __tablename__ = "articles"

    id           = Column(Integer, primary_key=True, index=True)
    feed_id      = Column(Integer, ForeignKey("feeds.id"), nullable=False)
    title        = Column(String, nullable=False)
    url          = Column(String, unique=True, nullable=False, index=True)
    author       = Column(String, nullable=True)
    content      = Column(Text, nullable=True)
    content_text = Column(Text, nullable=True)
    note         = Column(Text, nullable=True)   # personal reader note
    published_at = Column(DateTime, nullable=True)
    fetched_at   = Column(DateTime, server_default=func.now())
    is_read      = Column(Boolean, default=False)
    is_saved     = Column(Boolean, default=False)
    is_archived  = Column(Boolean, default=False)

    feed       = relationship("Feed", back_populates="articles")
    tags       = relationship("Tag", secondary=article_tags, back_populates="articles")
    highlights = relationship("Highlight", back_populates="article", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Article(id={self.id}, title='{self.title[:30]}...')>"
