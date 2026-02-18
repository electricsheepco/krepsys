"""Tag endpoints — add/remove tags on articles, list all tags."""

import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.database import get_db
from src.models.article import Article
from src.models.tag import Tag
from src.api.schemas import TagResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/articles", tags=["tags"])


@router.get("/tags/all", response_model=List[TagResponse])
def list_all_tags(db: Session = Depends(get_db)):
    """Return every tag that exists."""
    return db.query(Tag).order_by(Tag.name).all()


@router.post("/{article_id}/tags", response_model=List[TagResponse], status_code=status.HTTP_200_OK)
def add_tag(article_id: int, payload: dict, db: Session = Depends(get_db)):
    """Add a tag to an article by name. Creates the tag if it doesn't exist."""
    name = (payload.get("name") or "").strip().lower()
    if not name:
        raise HTTPException(status_code=400, detail="Tag name required")

    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    tag = db.query(Tag).filter(Tag.name == name).first()
    if not tag:
        tag = Tag(name=name)
        db.add(tag)
        db.flush()

    if tag not in article.tags:
        article.tags.append(tag)
        db.commit()

    return article.tags


@router.delete("/{article_id}/tags/{tag_name}", response_model=List[TagResponse])
def remove_tag(article_id: int, tag_name: str, db: Session = Depends(get_db)):
    """Remove a tag from an article."""
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    tag = db.query(Tag).filter(Tag.name == tag_name.lower()).first()
    if tag and tag in article.tags:
        article.tags.remove(tag)
        db.commit()

    return article.tags
