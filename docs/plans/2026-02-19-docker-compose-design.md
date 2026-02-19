# Docker Compose Design

**Date:** 2026-02-19
**Status:** Approved

## Goal

Single `docker compose up` deploys krepšys — backend + frontend — accessible at `http://localhost:8080`. No external dependencies required.

## Services

### backend
- Built from `backend/Dockerfile` (Python 3.12-slim)
- FastAPI on internal port 8001 (no host port — only reachable inside Docker network)
- SQLite persisted in named volume `krepsys_data` mounted at `/app/data`
- Env: `DATABASE_URL=sqlite:///./data/krepsys.db`, `ALLOWED_ORIGINS=http://localhost:8080`

### frontend
- Multi-stage Docker build:
  - Stage 1: `node:20-alpine` — runs `npm run build` with `VITE_API_URL=''`
  - Stage 2: `nginx:alpine` — serves built `dist/` on port 80
- nginx proxies `/api/` → `http://backend:8001`
- Exposes host port `8080:80`

## Code Change

`frontend/src/api/client.js`: change `||` → `??` for VITE_API_URL fallback.
- `''` (Docker) → uses relative URLs → nginx handles proxying
- Dev unchanged: `.env.local` explicitly sets `VITE_API_URL=http://localhost:8001`

## Files

| File | Action |
|------|--------|
| `docker-compose.yml` | New (project root) |
| `backend/Dockerfile` | New |
| `frontend/Dockerfile` | New |
| `frontend/nginx.conf` | New |
| `frontend/src/api/client.js` | `\|\|` → `??` |
| `/Volumes/zodlightning/automate/caddy/Caddyfile` | Add `krepsys.local` → `host.docker.internal:8080` |

## Personal Caddy Entry

```
http://krepsys.local:80 {
    reverse_proxy host.docker.internal:8080
}
```

## Usage

```bash
docker compose up -d        # start
docker compose down         # stop
docker compose logs -f      # logs
docker compose pull && docker compose up -d  # update
```
