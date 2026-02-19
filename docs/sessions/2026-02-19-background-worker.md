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
- Tests: 43 passing

## TODO (Next Session)
- [ ] Docker Compose + Caddy → `http://krepsys.local`
- [ ] Keyboard shortcuts: j/k navigate, r=read, s=save
- [ ] OPML import
- [ ] Full-text search
