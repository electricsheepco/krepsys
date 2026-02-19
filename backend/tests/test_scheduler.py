"""Tests for background scheduler logic."""

from datetime import datetime, timedelta, timezone
from src.models.feed import Feed
from src.utils.scheduler import _is_feed_due


def _make_feed(last_fetched=None, fetch_interval=900):
    feed = Feed(name="Test", url="https://example.com/feed.xml")
    feed.fetch_interval = fetch_interval
    feed.last_fetched = last_fetched
    return feed


def test_is_feed_due_never_fetched():
    feed = _make_feed(last_fetched=None)
    assert _is_feed_due(feed) is True


def test_is_feed_due_recently_fetched():
    feed = _make_feed(last_fetched=datetime.now(timezone.utc), fetch_interval=900)
    assert _is_feed_due(feed) is False


def test_is_feed_due_overdue():
    overdue = datetime.now(timezone.utc) - timedelta(seconds=1800)
    feed = _make_feed(last_fetched=overdue, fetch_interval=900)
    assert _is_feed_due(feed) is True


def test_is_feed_due_exactly_at_interval():
    # At exactly fetch_interval seconds ago, it's due
    due = datetime.now(timezone.utc) - timedelta(seconds=900)
    feed = _make_feed(last_fetched=due, fetch_interval=900)
    assert _is_feed_due(feed) is True


def test_is_feed_due_naive_datetime():
    # DB may return naive datetime — should still work
    naive = datetime.utcnow() - timedelta(seconds=1800)
    feed = _make_feed(last_fetched=naive, fetch_interval=900)
    assert _is_feed_due(feed) is True
