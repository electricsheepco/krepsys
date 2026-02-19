# Background Worker Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Auto-refetch all feeds on a per-feed interval so new articles appear without manual user action.

**Architecture:** An `asyncio.Task` started in the FastAPI lifespan wakes every 60 seconds, queries active feeds, checks `last_fetched` against each feed's `fetch_interval`, and runs `fetch_feed()` (in a thread executor) for any feeds that are due. Each scheduled fetch gets its own DB session to stay thread-safe.

**Tech Stack:** Python asyncio, SQLAlchemy (existing), feedparser (existing), pytest + unittest.mock

---

### Task 1: Update `fetch_feed()` to write `last_fetched`

**Files:**
- Modify: `backend/src/utils/fetcher.py`
- Test: `backend/tests/test_fetcher.py` (new)

**Step 1: Write the failing test**

Create `backend/tests/test_fetcher.py`:

```python
"""Tests for fetch_feed utility."""

from unittest.mock import patch
from datetime import timezone
from tests.conftest import TestingSessionLocal
from src.models.feed import Feed
from src.utils.fetcher import fetch_feed


EMPTY_FEED = {
    "entries": [],
    "bozo": False,
}


def test_fetch_feed_sets_last_fetched(setup_database):
    db = TestingSessionLocal()
    feed = Feed(name="Test", url="https://example.com/feed.xml")
    db.add(feed)
    db.commit()
    db.refresh(feed)
    feed_id = feed.id
    db.close()

    with patch("src.utils.fetcher.feedparser.parse", return_value=EMPTY_FEED):
        db2 = TestingSessionLocal()
        fetch_feed(feed_id, "https://example.com/feed.xml", db2)
        db2.refresh(feed := db2.query(Feed).filter(Feed.id == feed_id).first())
        assert feed.last_fetched is not None
        assert feed.last_fetched.tzinfo == timezone.utc
        db2.close()
```

**Step 2: Run the test to confirm it fails**

```bash
cd /Volumes/zodlightning/automate/krepsys/backend
source venv/bin/activate
pytest tests/test_fetcher.py -v
```

Expected: FAIL — `AssertionError: assert None is not None`

**Step 3: Update `fetch_feed()` to write `last_fetched`**

In `backend/src/utils/fetcher.py`, add the `Feed` import and update `last_fetched` at the end of the function.

Add to imports:
```python
from src.models.feed import Feed
```

Replace the final `return new_count` with:
```python
    feed_obj = db.query(Feed).filter(Feed.id == feed_id).first()
    if feed_obj:
        feed_obj.last_fetched = datetime.now(timezone.utc)
        db.commit()

    return new_count
```

**Step 4: Run test to confirm it passes**

```bash
pytest tests/test_fetcher.py -v
```

Expected: PASS

**Step 5: Confirm existing tests still pass**

```bash
pytest tests/ -v
```

Expected: all existing tests pass

**Step 6: Commit**

```bash
git add backend/src/utils/fetcher.py backend/tests/test_fetcher.py
git commit -m "feat: fetch_feed writes last_fetched after each fetch"
```

---

### Task 2: Create `scheduler.py`

**Files:**
- Create: `backend/src/utils/scheduler.py`
- Test: `backend/tests/test_scheduler.py` (new)

**Step 1: Write the failing tests**

Create `backend/tests/test_scheduler.py`:

```python
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
```

**Step 2: Run the tests to confirm they fail**

```bash
pytest tests/test_scheduler.py -v
```

Expected: FAIL — `ImportError: cannot import name '_is_feed_due' from 'src.utils.scheduler'`

**Step 3: Create `scheduler.py`**

Create `backend/src/utils/scheduler.py`:

```python
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
```

**Step 4: Run the tests to confirm they pass**

```bash
pytest tests/test_scheduler.py -v
```

Expected: all 5 tests PASS

**Step 5: Commit**

```bash
git add backend/src/utils/scheduler.py backend/tests/test_scheduler.py
git commit -m "feat: add background scheduler with per-feed interval logic"
```

---

### Task 3: Wire scheduler into the lifespan

**Files:**
- Modify: `backend/src/main.py`

**Step 1: No new tests needed** — the scheduler's unit behaviour is tested. The wiring is integration-level and verified manually by running the server.

**Step 2: Add scheduler import to `main.py`**

At the top of `backend/src/main.py`, add:

```python
import asyncio
from src.utils.scheduler import run_scheduler
```

**Step 3: Start and stop the task in the lifespan**

Replace the existing lifespan `yield` block:

```python
    yield

    # Shutdown
    logger.info("Shutting down Krepsys application")
```

With:

```python
    # Start background feed scheduler
    scheduler_task = asyncio.create_task(run_scheduler())
    logger.info("Background scheduler started")

    yield

    # Shutdown
    scheduler_task.cancel()
    try:
        await scheduler_task
    except asyncio.CancelledError:
        pass
    logger.info("Shutting down Krepsys application")
```

**Step 4: Run all tests to confirm nothing broke**

```bash
pytest tests/ -v
```

Expected: all tests pass

**Step 5: Smoke-test the running server**

Start the server and watch logs:

```bash
uvicorn src.main:app --reload --port 8001
```

Expected log output within first minute:
```
{"message": "Scheduler started (tick interval: 60s)", ...}
```

After 60s, if any feeds have `last_fetched = NULL`:
```
{"message": "Scheduler: N feed(s) due for refresh", ...}
```

**Step 6: Commit**

```bash
git add backend/src/main.py
git commit -m "feat: start background scheduler in app lifespan"
```

---

### Task 4: Update docs

**Files:**
- Modify: `docs/sessions/` — new session note
- Modify: `docs/ideas.md` — mark background worker done

**Step 1: Mark the idea done in `docs/ideas.md`**

Change:
```
- [ ] RSS fetching worker (background sync on interval)
```
To:
```
- [x] RSS fetching worker (background sync on interval)
```

**Step 2: Write session note to `docs/sessions/2026-02-19-background-worker.md`**

```markdown
# 2026-02-19 - Background Worker

## What Got Done
- [x] `fetch_feed()` now writes `last_fetched` after every fetch
- [x] `src/utils/scheduler.py` — async loop, wakes every 60s, fetches due feeds
- [x] Wired into FastAPI lifespan — starts on boot, cancels on shutdown
- [x] Per-feed `fetch_interval` respected (default 900s)
- [x] Naive datetime handling for SQLite-stored timestamps
- [x] Each scheduled fetch gets its own DB session (thread-safe)

## State at Session End
- Scheduler runs automatically on `uvicorn` start
- Manual refresh (`POST /api/feeds/{id}/refresh`) also updates `last_fetched`
- Tests: all passing

## TODO (Next Session)
- [ ] Docker Compose + Caddy → `http://krepsys.local`
- [ ] Keyboard shortcuts: j/k navigate, r=read, s=save
- [ ] OPML import
- [ ] Full-text search
```

**Step 3: Commit**

```bash
git add docs/sessions/2026-02-19-background-worker.md docs/ideas.md
git commit -m "docs: session notes for background worker"
```
