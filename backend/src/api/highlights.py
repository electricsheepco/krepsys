"""Highlight endpoints — create, list, update, delete highlights on articles."""

import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.database import get_db
from src.models.article import Article
from src.models.highlight import Highlight
from src.api.schemas import HighlightCreate, HighlightUpdate, HighlightResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/articles", tags=["highlights"])


@router.get("/{article_id}/highlights", response_model=List[HighlightResponse])
def list_highlights(article_id: int, db: Session = Depends(get_db)):
    return db.query(Highlight).filter(Highlight.article_id == article_id).all()


@router.post("/{article_id}/highlights", response_model=HighlightResponse, status_code=status.HTTP_201_CREATED)
def create_highlight(article_id: int, payload: HighlightCreate, db: Session = Depends(get_db)):
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    highlight = Highlight(
        article_id=article_id,
        text=payload.text,
        color=payload.color,
        note=payload.note,
    )
    db.add(highlight)
    db.commit()
    db.refresh(highlight)
    logger.info(f"Created highlight id={highlight.id} on article {article_id}")
    return highlight


@router.patch("/highlights/{highlight_id}", response_model=HighlightResponse)
def update_highlight(highlight_id: int, payload: HighlightUpdate, db: Session = Depends(get_db)):
    h = db.query(Highlight).filter(Highlight.id == highlight_id).first()
    if not h:
        raise HTTPException(status_code=404, detail="Highlight not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(h, field, value)
    db.commit()
    db.refresh(h)
    return h


@router.delete("/highlights/{highlight_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_highlight(highlight_id: int, db: Session = Depends(get_db)):
    h = db.query(Highlight).filter(Highlight.id == highlight_id).first()
    if not h:
        raise HTTPException(status_code=404, detail="Highlight not found")
    db.delete(h)
    db.commit()
