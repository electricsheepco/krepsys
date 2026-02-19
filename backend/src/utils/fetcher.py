"""RSS/Atom feed fetcher."""

import logging
from datetime import datetime, timezone
import feedparser
from sqlalchemy.orm import Session
from src.models.article import Article
from src.models.feed import Feed

logger = logging.getLogger(__name__)


def fetch_feed(feed_id: int, feed_url: str, db: Session) -> int:
    """Fetch a feed and store new articles. Returns count of new articles added."""
    try:
        parsed = feedparser.parse(feed_url)
    except Exception as e:
        logger.error(f"Failed to fetch feed {feed_url}: {e}")
        return 0

    if parsed.bozo and not parsed.entries:
        logger.warning(f"Feed parse error for {feed_url}: {parsed.bozo_exception}")
        return 0

    new_count = 0
    for entry in parsed.entries:
        url = entry.get("link")
        if not url:
            continue

        # Skip if already stored
        if db.query(Article).filter(Article.url == url).first():
            continue

        # Extract content — prefer full content over summary
        content = None
        if entry.get("content"):
            content = entry.content[0].get("value")
        if not content:
            content = entry.get("summary")

        # Parse published date
        published_at = None
        if entry.get("published_parsed"):
            try:
                published_at = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            except Exception:
                pass

        article = Article(
            feed_id=feed_id,
            title=entry.get("title", "Untitled"),
            url=url,
            author=entry.get("author"),
            content=content,
            content_text=None,
            published_at=published_at,
        )
        db.add(article)
        new_count += 1

    if new_count:
        db.commit()
        logger.info(f"Feed {feed_url}: added {new_count} new articles")

    feed_obj = db.query(Feed).filter(Feed.id == feed_id).first()
    if feed_obj:
        feed_obj.last_fetched = datetime.now(timezone.utc)
        db.commit()

    return new_count
