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

# Run tests
uv run pytest

# Run a single test file or test
uv run pytest tests/test_routes.py
uv run pytest tests/test_routes.py::test_name -v

# Run tests with coverage
uv run pytest --cov=app --cov-report=term-missing

# Docker
docker compose up
```

## Architecture

Flask app using the application factory pattern (`app/__init__.py` → `create_app()`), organized into three blueprints:

- **`app/events/`** — main UI (`GET /`) and event submission (`POST /submit`)
- **`app/settings/`** — alias CRUD (`GET/POST /settings`) and calendar listing (`GET /list-calendars`)
- **`app/auth/`** — Google OAuth via Flask-Dance (`/login/google`), auto-creates users on first sign-in

### Auth & Data Model (`app/models.py`)

Uses Flask-SQLAlchemy with SQLite (`data/app.db`). Three models:
- **`User`** — email, name; created automatically on first Google sign-in
- **`OAuth`** (Flask-Dance's `OAuthConsumerMixin`) — stores OAuth tokens per user in the DB
- **`CalendarAlias`** — per-user alias→calendar ID mappings (unique constraint on user+alias)

Flask-Login manages sessions. Flask-Dance's `google_bp` handles the full OAuth flow and stores tokens via `SQLAlchemyStorage`.

### Core Services (`app/services/`)

- **`calendar_client.py`** — `build_service_for_user(token)` converts a Flask-Dance token dict into a Google Calendar API service; `create_event_quick_add()` uses Google's natural language `quickAdd` endpoint.
- **`alias_parser.py`** — parses `@alias` prefixes from event text lines, resolves aliases to calendar IDs from the database. Defaults to `"primary"` when no alias is present.
- **`list_calendars.py`** — fetches all calendars from the API; usable as CLI (`uv run -m app.services.list_calendars`) or called from settings routes.

### Data Flow

User submits textarea (one event per line) → each line is parsed for `@alias` prefix → alias resolved to calendar ID via user's `CalendarAlias` records → `quickAdd` API call per event → results stored in Flask session (capped at 50).

### Environment Variables

- `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` — OAuth credentials (required)
- `SECRET_KEY` — Flask session key (defaults to dev key)
- `ALLOW_INSECURE_OAUTH_TRANSPORT=1` — allow OAuth over HTTP for local dev
- `TRUST_PROXY_HEADERS=1` — enable `ProxyFix` when behind a TLS-terminating reverse proxy

### Notes
- Frontend uses only Tailwind CSS (CDN) and vanilla JS — no build step
- `data/` directory is gitignored; contains `app.db` at runtime

## Testing

Tests in `tests/` using pytest with `pytest-mock`. No real API credentials needed.

Key fixtures in `conftest.py`:
- `app` — creates app with in-memory SQLite (`sqlite:///:memory:`)
- `logged_in_client` — test client with an authenticated user session (uses `make_logged_in_client` helper)
- `mock_google_token` / `mock_calendar_service` — mocks Flask-Dance's `google` object and `build_service_for_user`
- `user_aliases` — pre-populates `CalendarAlias` records for the test user
