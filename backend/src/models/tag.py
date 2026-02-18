"""Tag model for article labeling."""

from sqlalchemy import Column, Integer, String, Table, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.database import Base

# M2M junction table
article_tags = Table(
    "article_tags",
    Base.metadata,
    Column("article_id", Integer, ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id",     Integer, ForeignKey("tags.id",     ondelete="CASCADE"), primary_key=True),
)


class Tag(Base):
    __tablename__ = "tags"

    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())

    articles = relationship("Article", secondary=article_tags, back_populates="tags")
