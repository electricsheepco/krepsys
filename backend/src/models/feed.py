"""Feed model for storing RSS feed information."""

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.database import Base


class Feed(Base):
    """RSS feed model."""

    __tablename__ = "feeds"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    url = Column(String, unique=True, nullable=False, index=True)
    fetch_interval = Column(Integer, default=900)  # seconds
    last_fetched = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relationship to articles
    articles = relationship("Article", back_populates="feed", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Feed(id={self.id}, name='{self.name}')>"
