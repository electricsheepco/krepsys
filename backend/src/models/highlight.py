"""Highlight model for saving selected text from articles."""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.database import Base


class Highlight(Base):
    __tablename__ = "highlights"

    id         = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False)
    text       = Column(Text, nullable=False)
    color      = Column(String, default="yellow", nullable=False)  # yellow | green | blue | pink
    note       = Column(Text, nullable=True)   # optional note on this specific highlight
    created_at = Column(DateTime, server_default=func.now())

    article = relationship("Article", back_populates="highlights")
