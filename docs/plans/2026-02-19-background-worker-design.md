# Background Worker Design

**Date:** 2026-02-19
**Status:** Approved

## Goal

Auto-refetch all feeds on a background interval so new articles appear without manual refresh.

## Approach

asyncio loop — no new dependencies, lives in the FastAPI lifespan context manager.
Wakes every 60 seconds, checks which feeds are due, and dispatches fetches for those feeds.

## Components

| File | Change |
|------|--------|
| `src/utils/scheduler.py` | New. Async loop — wakes every 60s, checks due feeds, dispatches fetches |
| `src/utils/fetcher.py` | Update. Write `feed.last_fetched = utcnow()` after successful fetch |
| `src/main.py` | Update. `asyncio.create_task(run_scheduler())` in lifespan; task cancelled on shutdown |
| `src/api/feeds.py` | No change. Manual refresh calls `fetch_feed()` which now writes `last_fetched` |

## Data Flow (per tick)

1. Open a fresh DB session
2. Query all feeds where `is_active = True`
3. For each feed: fetch if `last_fetched is None` OR `now - last_fetched >= fetch_interval`
4. Call `fetch_feed()` via `run_in_executor` (sync fn, avoid blocking event loop)
5. Close DB session

## Error Handling

- Individual feed errors: already swallowed and logged in `fetch_feed()` — won't kill the loop
- Tick body wrapped in `try/except Exception` — bad DB query can't crash the scheduler
- `asyncio.CancelledError` propagates cleanly on shutdown (not caught)

## Interval

- Per-feed `fetch_interval` field (seconds, default 900 = 15 min)
- Worker check cadence: every 60 seconds
- On startup: respects `last_fetched` — only fetches feeds that are actually due

## Testing

- Unit: "is feed due?" logic (never fetched, just fetched, overdue)
- Integration: seed feed with `last_fetched = None`, run one tick, assert `last_fetched` set + articles exist
- Mock `feedparser.parse` to avoid real HTTP
