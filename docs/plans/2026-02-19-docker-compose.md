# Docker Compose Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add Docker Compose support so `docker compose up` serves the full krepšys app at `http://localhost:8080`.

**Architecture:** Two containers — `backend` (FastAPI/Python) and `frontend` (nginx serving built React + proxying `/api/` to backend). SQLite persisted in a named Docker volume. nginx is the single entry point on port 8080; no Caddy required for public users.

**Tech Stack:** Docker Compose, Python 3.12-slim, node:20-alpine, nginx:alpine

---

### Task 1: Fix API client for relative URL support

**Files:**
- Modify: `frontend/src/api/client.js:4`

No test needed — this is a 1-character change verified by the Docker smoke test in Task 5.

**Step 1: Make the change**

In `frontend/src/api/client.js`, change line 4 from:
```js
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8080',
```
To:
```js
  baseURL: import.meta.env.VITE_API_URL ?? '',
```

`??` (nullish coalescing) only falls back when the value is `null` or `undefined`. An empty string `''` is treated as valid — meaning "use relative URLs". Dev is unchanged: `.env.local` still sets `VITE_API_URL=http://localhost:8001` explicitly.

**Step 2: Verify dev still works**

```bash
cd /Volumes/zodlightning/automate/krepsys/frontend
cat .env.local
```

Expected: `VITE_API_URL=http://localhost:8001` — still set, dev unaffected.

**Step 3: Commit**

```bash
cd /Volumes/zodlightning/automate/krepsys
git add frontend/src/api/client.js
git commit -m "fix: use nullish coalescing for VITE_API_URL to support relative URLs"
```

---

### Task 2: Create `backend/Dockerfile`

**Files:**
- Create: `backend/Dockerfile`

**Step 1: Create the file**

Create `backend/Dockerfile`:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY src/ ./src/

# Create data directory for SQLite
RUN mkdir -p /app/data

# Run as non-root
RUN useradd -m appuser && chown -R appuser /app
USER appuser

EXPOSE 8001

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

**Step 2: Verify it builds**

```bash
cd /Volumes/zodlightning/automate/krepsys/backend
docker build -t krepsys-backend .
```

Expected: `Successfully built ...` with no errors.

**Step 3: Commit**

```bash
cd /Volumes/zodlightning/automate/krepsys
git add backend/Dockerfile
git commit -m "feat: add backend Dockerfile"
```

---

### Task 3: Create `frontend/nginx.conf`

**Files:**
- Create: `frontend/nginx.conf`

**Step 1: Create the file**

Create `frontend/nginx.conf`:

```nginx
server {
    listen 80;

    root /usr/share/nginx/html;
    index index.html;

    # Proxy API requests to backend container
    location /api/ {
        proxy_pass http://backend:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # SPA routing — serve index.html for all non-file routes
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

**Step 2: Commit**

```bash
cd /Volumes/zodlightning/automate/krepsys
git add frontend/nginx.conf
git commit -m "feat: add nginx config for frontend container"
```

---

### Task 4: Create `frontend/Dockerfile`

**Files:**
- Create: `frontend/Dockerfile`

**Step 1: Create the file**

Create `frontend/Dockerfile`:

```dockerfile
# Stage 1: Build React app
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

# Build with empty VITE_API_URL — axios will use relative URLs
# nginx proxies /api/ to the backend container
ARG VITE_API_URL=""
ENV VITE_API_URL=${VITE_API_URL}

RUN npm run build

# Stage 2: Serve with nginx
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
```

**Step 2: Verify it builds standalone**

```bash
cd /Volumes/zodlightning/automate/krepsys/frontend
docker build -t krepsys-frontend .
```

Expected: `Successfully built ...` — two stages complete, no errors.

**Step 3: Commit**

```bash
cd /Volumes/zodlightning/automate/krepsys
git add frontend/Dockerfile
git commit -m "feat: add multi-stage frontend Dockerfile"
```

---

### Task 5: Create `docker-compose.yml` and smoke test

**Files:**
- Create: `docker-compose.yml` (project root)

**Step 1: Create the file**

Create `/Volumes/zodlightning/automate/krepsys/docker-compose.yml`:

```yaml
services:
  backend:
    build: ./backend
    volumes:
      - krepsys_data:/app/data
    environment:
      DATABASE_URL: sqlite:///./data/krepsys.db
      ALLOWED_ORIGINS: http://localhost:8080
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "8080:80"
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  krepsys_data:
```

**Step 2: Build both images**

```bash
cd /Volumes/zodlightning/automate/krepsys
docker compose build
```

Expected: both `backend` and `frontend` build successfully, no errors.

**Step 3: Start the stack**

```bash
docker compose up -d
```

Expected:
```
✔ Container krepsys-backend-1   Started
✔ Container krepsys-frontend-1  Started
```

**Step 4: Smoke test**

```bash
# Frontend loads
curl -s -o /dev/null -w "%{http_code}" http://localhost:8080
```
Expected: `200`

```bash
# API reachable through nginx proxy
curl -s http://localhost:8080/api/feeds
```
Expected: `[]` (empty array — no feeds yet, but 200 OK)

```bash
# Health check
curl -s http://localhost:8080/api/health
```
Expected: `{"status":"healthy","database":"connected","version":"0.1.0"}`

**Step 5: Stop the stack**

```bash
docker compose down
```

**Step 6: Commit**

```bash
cd /Volumes/zodlightning/automate/krepsys
git add docker-compose.yml
git commit -m "feat: add docker-compose.yml for one-command deploy"
```

---

### Task 6: Update Caddyfile for `krepsys.local`

**Files:**
- Modify: `/Volumes/zodlightning/automate/caddy/Caddyfile`

This is a local-only task — not committed to the krepsys repo (Caddy is a separate service).

**Step 1: Add the krepsys entry**

In `/Volumes/zodlightning/automate/caddy/Caddyfile`, add after the existing entries:

```
# krepšys - RSS reader
http://krepsys.local:80 {
    reverse_proxy host.docker.internal:8080
}
```

**Step 2: Reload Caddy**

```bash
docker exec $(docker ps -qf "name=caddy") caddy reload --config /etc/caddy/Caddyfile
```

Expected: no output (success) or `caddy: reloaded`

**Step 3: Verify**

Start krepsys first if not running:
```bash
cd /Volumes/zodlightning/automate/krepsys && docker compose up -d
```

Then:
```bash
curl -s -o /dev/null -w "%{http_code}" http://krepsys.local
```
Expected: `200`

---

### Task 7: Update `.dockerignore` and docs

**Files:**
- Create: `backend/.dockerignore`
- Create: `frontend/.dockerignore`
- Modify: `docs/ideas.md`
- Create: `docs/sessions/2026-02-19-docker-compose.md`

**Step 1: Create `backend/.dockerignore`**

```
venv/
__pycache__/
*.pyc
*.pyo
tests/
.env
*.db
data/
```

**Step 2: Create `frontend/.dockerignore`**

```
node_modules/
dist/
.env*
```

**Step 3: Mark idea done in `docs/ideas.md`**

Change:
```
- [ ] Docker Compose setup for one-command deploy
```
To:
```
- [x] Docker Compose setup for one-command deploy
```

Also change:
```
- [ ] Caddy reverse proxy config → `http://krepsys.local`
```
To:
```
- [x] Caddy reverse proxy config → `http://krepsys.local`
```

**Step 4: Write session note**

Create `docs/sessions/2026-02-19-docker-compose.md`:

```markdown
# 2026-02-19 - Docker Compose

## What Got Done
- [x] `backend/Dockerfile` — Python 3.12-slim, runs as non-root user
- [x] `frontend/Dockerfile` — multi-stage: node:20-alpine build → nginx:alpine serve
- [x] `frontend/nginx.conf` — serves React SPA, proxies `/api/` → backend container
- [x] `docker-compose.yml` — two services, named volume for SQLite, port 8080
- [x] `frontend/src/api/client.js` — `||` → `??` for relative URL support
- [x] Caddyfile updated — `http://krepsys.local` → `host.docker.internal:8080`

## How to Run
```bash
docker compose up -d   # start at http://localhost:8080
docker compose down    # stop
```

## State at Session End
- Public GitHub: https://github.com/electricsheepco/krepsys
- docker compose up → http://localhost:8080 ✓
- http://krepsys.local ✓ (personal Caddy)

## TODO (Next Session)
- [ ] Keyboard shortcuts: j/k navigate, r=read, s=save
- [ ] OPML import
- [ ] Full-text search
```

Also write the same to:
`/Volumes/zodlightning/Loop/moebius/01 Projects/essco/krepsys/2026-02-19-docker-compose.md`

**Step 5: Commit**

```bash
cd /Volumes/zodlightning/automate/krepsys
git add backend/.dockerignore frontend/.dockerignore docs/ideas.md docs/sessions/2026-02-19-docker-compose.md
git commit -m "docs: docker compose session notes and dockerignore files"
```

**Step 6: Push to GitHub**

```bash
cd /Volumes/zodlightning/automate/krepsys
git push
```
