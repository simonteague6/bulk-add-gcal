# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
uv sync

# Run development server (port 5485)
uv run run.py

# Lint and format
uvx ruff check .
uvx ruff format .

# List user's Google Calendar IDs (useful for configuring aliases)
uv run -m app.services.list_calendars

# Docker
docker compose up
```

No automated test suite exists.

## Architecture

Flask app using the application factory pattern (`app/__init__.py` → `create_app()`), organized into three blueprints:

- **`app/events/`** — main UI (`GET /`) and event submission (`POST /submit`)
- **`app/settings/`** — alias CRUD (`GET/POST /settings`) and calendar listing (`GET /list-calendars`)
- **`app/auth/`** — OAuth routes (stubbed, not yet implemented)

### Core Services (`app/services/`)

- **`calendar_client.py`** — Google Calendar API integration. `load_credentials()` manages `token.json` (OAuth token persistence); `create_event_quick_add()` uses Google's natural language parser to create events.
- **`alias_parser.py`** — parses `@alias` prefixes from event text lines, maps them to calendar IDs via `data/calendar_aliases.json`. Defaults to `"primary"` when no alias is present.
- **`list_calendars.py`** — fetches all calendars from the API; usable as CLI or called from settings routes.

### Data Flow

User submits textarea (one event per line) → each line is parsed for `@alias` prefix → alias resolved to calendar ID → `quickAdd` API call per event → results stored in Flask session (capped at 50).

### Runtime Data (`data/`)

- `credentials.json` — Google OAuth credentials (not in git, must be created manually)
- `token.json` — OAuth tokens (not in git, auto-created on first auth)
- `calendar_aliases.json` — user alias config (not in git, managed via Settings UI)

### Notes

- Current OAuth uses `InstalledAppFlow` (desktop mode); migration to web server flow is planned (Issue #5)
- Flask `SECRET_KEY` defaults to a dev key; set via env var for production
- Frontend uses only Tailwind CSS (CDN) and vanilla JS — no build step
