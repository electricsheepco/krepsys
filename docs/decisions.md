# Architecture Decisions

## ADR-001: SQLite over PostgreSQL
**Date:** 2026-02
**Decision:** Use SQLite as the database.
**Reason:** Single-user, self-hosted app. SQLite is sufficient, zero ops, no separate container needed. Can migrate later if needed.

## ADR-002: FastAPI over Django/Flask
**Date:** 2026-02
**Decision:** FastAPI for the backend.
**Reason:** Async support, auto-generated OpenAPI docs, Pydantic validation built-in, fast to iterate.

## ADR-003: TanStack Query over SWR/Redux
**Date:** 2026-02
**Decision:** TanStack Query v5 for client state.
**Reason:** Best-in-class server state management. Handles caching, invalidation, and mutations cleanly.

## ADR-004: Three-column layout
**Date:** 2026-02
**Decision:** Sidebar (feeds/filters) | Article List | Article Reader - fixed 3-column layout.
**Reason:** Mirrors familiar newsletter/email client UX (Reeder, Readwise Reader, Apple Mail).

## ADR-005: Tailwind v4
**Date:** 2026-02
**Decision:** Use Tailwind CSS v4 with `@tailwindcss/postcss`.
**Context:** v4 breaks v3 PostCSS config. Requires `@import "tailwindcss"` in CSS and `@tailwindcss/postcss` plugin.
