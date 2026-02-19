"""Tests for fetch_feed utility."""

from unittest.mock import patch
from datetime import datetime, timezone
import feedparser
from tests.conftest import TestingSessionLocal
from src.models.feed import Feed
from src.utils.fetcher import fetch_feed


EMPTY_FEED = feedparser.FeedParserDict({"entries": [], "bozo": False})


def test_fetch_feed_sets_last_fetched(setup_database):
    db = TestingSessionLocal()
    feed = Feed(name="Test", url="https://example.com/feed.xml")
    db.add(feed)
    db.commit()
    db.refresh(feed)
    feed_id = feed.id
    db.close()

    before = datetime.now(timezone.utc).replace(tzinfo=None)
    with patch("src.utils.fetcher.feedparser.parse", return_value=EMPTY_FEED):
        db2 = TestingSessionLocal()
        fetch_feed(feed_id, "https://example.com/feed.xml", db2)
        feed = db2.query(Feed).filter(Feed.id == feed_id).first()
        # SQLite stores datetimes without tzinfo, so we compare naive UTC values.
        assert feed.last_fetched is not None
        assert feed.last_fetched >= before
        db2.close()
