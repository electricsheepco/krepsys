# Ideas & Feature Backlog

## High Priority
- [ ] Add feed via URL (UI form in Sidebar)
- [x] RSS fetching worker (background sync on interval)
- [ ] Kill the Newsletter integration (email-to-RSS)
- [ ] Docker Compose setup for one-command deploy

## UI/UX
- [ ] Keyboard shortcuts (j/k to navigate, r to mark read, s to save)
- [ ] Reading progress indicator
- [ ] Font size / line width controls in reader
- [ ] Dark mode
- [ ] Article count badges on feed list items

## Features
- [ ] OPML import/export (migrate from other readers)
- [ ] Full-text search across articles
- [ ] Reading time estimate
- [ ] Highlight + annotation support (the Readwise differentiator)
- [ ] Daily digest email (summary of saved articles)
- [ ] Share article (copy link button)

## Infrastructure
- [ ] Caddy reverse proxy config → `http://krepsys.local`
- [ ] Persistent Docker volume for SQLite db
- [ ] Health check endpoint
- [ ] Auto-backup of SQLite to Proton Drive

## Integrations
- [ ] Readwise export (CSV/JSON)
- [ ] Obsidian integration (save highlights to vault)
- [ ] n8n webhook on new article
