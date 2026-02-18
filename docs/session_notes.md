# Session Notes

## 2026-02-18

### Done
- Initialized git repo with initial commit
- Fixed Tailwind v4 breakage:
  - Installed `@tailwindcss/postcss`
  - Updated `postcss.config.js` to use `@tailwindcss/postcss`
  - Updated `index.css` to use `@import "tailwindcss"` + `@plugin "@tailwindcss/typography"`
  - Build now passes (131 modules, clean)
- Created project documentation:
  - `CLAUDE.md` - project context for Claude sessions
  - `docs/decisions.md` - architecture decision records
  - `docs/ideas.md` - feature backlog
  - `docs/session_notes.md` - this file
- Backend: 37 tests passing

### State at Session End
- Frontend builds clean, Vite dev server runs
- 3-column layout: Sidebar + ArticleList + ArticleReader all wired up
- TanStack Query hooks: `useFeeds`, `useArticles`, `useArticle`, `useUpdateArticle`
- No Docker setup yet, no OPML import, no RSS worker UI

### Next
- Continue frontend work (pick up where we left off before the break)
