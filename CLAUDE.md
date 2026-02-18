# Krepsys - Claude Code Project Notes

## What This Is
Self-hosted newsletter/RSS reader. Get newsletters out of email into a clean reading app.
Built from scratch. MIT license. Runs locally via Docker.

## Stack
- **Backend**: Python + FastAPI + SQLite (SQLAlchemy) + APScheduler
- **Frontend**: React 19 + Vite 7 + Tailwind v4 + TanStack Query v5 + Axios
- **Infra**: Docker + Caddy reverse proxy → `http://krepsys.local`

## Running Locally (Dev)

```bash
# Backend
cd backend
source venv/bin/activate
uvicorn src.main:app --reload --port 8001

# Frontend (separate terminal)
cd frontend
npm run dev
```

Backend API: `http://localhost:8001`
Frontend: `http://localhost:18300` (Vite picks port)

## Key Files

```
krepsys/
├── backend/
│   ├── src/
│   │   ├── main.py          # FastAPI app entry
│   │   ├── database.py      # SQLAlchemy setup
│   │   ├── config.py        # Settings
│   │   ├── api/
│   │   │   ├── feeds.py     # Feed CRUD endpoints
│   │   │   ├── articles.py  # Article CRUD + filtering endpoints
│   │   │   └── schemas.py   # Pydantic schemas
│   │   ├── models/
│   │   │   ├── feed.py      # Feed ORM model
│   │   │   └── article.py   # Article ORM model
│   │   ├── utils/           # RSS fetching, content parsing
│   │   └── workers/         # Background feed sync jobs
│   └── tests/               # 37 tests, all pass
│       ├── test_api_articles.py
│       ├── test_api_feeds.py
│       └── ...
└── frontend/
    └── src/
        ├── App.jsx          # Root layout (3-column: Sidebar | List | Reader)
        ├── components/
        │   ├── Sidebar.jsx      # Feed list + filter nav
        │   ├── ArticleList.jsx  # Article list panel
        │   └── ArticleReader.jsx # Reading pane with toolbar
        └── hooks/
            ├── useFeeds.js      # TanStack Query hooks for feeds
            └── useArticles.js   # TanStack Query hooks for articles

```

## Running Tests

```bash
cd backend
source venv/bin/activate
pytest tests/ -v
```

## Tailwind v4 Notes
- Uses `@tailwindcss/postcss` (NOT the old `tailwindcss` PostCSS plugin)
- CSS uses `@import "tailwindcss"` (NOT `@tailwind base/components/utilities`)
- Typography plugin: `@plugin "@tailwindcss/typography"` in CSS
- `tailwind.config.js` is essentially unused in v4 PostCSS mode

## Docs
- `docs/decisions.md` - Architecture decisions
- `docs/ideas.md` - Feature ideas backlog
- `docs/session_notes.md` - Per-session progress log
