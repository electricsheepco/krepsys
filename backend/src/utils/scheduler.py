"""Background scheduler for periodic feed fetching."""

import asyncio
import logging
from datetime import datetime, timezone
from src.database import SessionLocal
from src.models.feed import Feed
from src.utils.fetcher import fetch_feed

logger = logging.getLogger(__name__)

TICK_INTERVAL = 60  # seconds


def _is_feed_due(feed: Feed) -> bool:
    """Return True if the feed is due for a fetch."""
    if feed.last_fetched is None:
        return True
    last = feed.last_fetched
    if last.tzinfo is None:
        last = last.replace(tzinfo=timezone.utc)
    elapsed = (datetime.now(timezone.utc) - last).total_seconds()
    return elapsed >= feed.fetch_interval


def _fetch_feed_with_session(feed_id: int, feed_url: str) -> int:
    """Fetch a feed in its own DB session (safe for thread executor use)."""
    db = SessionLocal()
    try:
        return fetch_feed(feed_id, feed_url, db)
    finally:
        db.close()


async def run_scheduler() -> None:
    """Background task: checks and fetches due feeds every TICK_INTERVAL seconds."""
    logger.info("Scheduler started (tick interval: %ds)", TICK_INTERVAL)
    loop = asyncio.get_event_loop()
    while True:
        try:
            await asyncio.sleep(TICK_INTERVAL)
            db = SessionLocal()
            try:
                due = [
                    f for f in db.query(Feed).filter(Feed.is_active == True).all()
                    if _is_feed_due(f)
                ]
            finally:
                db.close()

            if due:
                logger.info("Scheduler: %d feed(s) due for refresh", len(due))
            for feed in due:
                await loop.run_in_executor(
                    None, _fetch_feed_with_session, feed.id, feed.url
                )
        except asyncio.CancelledError:
            logger.info("Scheduler shutting down")
            raise
        except Exception:
            logger.exception("Scheduler tick error (continuing)")
