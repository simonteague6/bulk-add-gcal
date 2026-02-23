# Bulk Calendar

A Python Flask web application for bulk Google Calendar event creation using natural language processing. Create multiple events at once by typing them in plain English, with support for routing events to different calendars using simple aliases.

## Features

- **Bulk Event Creation**: Add multiple events at once, one per line
- **Natural Language Processing**: Use Google's quickAdd API to parse event text like "Dinner with Sarah at 7pm tomorrow"
- **Calendar Aliases**: Route events to specific calendars using `@alias` syntax (e.g., `@workout Push day Monday 7pm`)
- **Web Interface**: Clean, modern UI for managing events and aliases
- **CLI Tool**: Command-line interface for quick event creation
- **OAuth Authentication**: Secure Google Calendar API integration

## Quick Start

### Prerequisites

- Python 3.14+
- [uv](https://github.com/astral-sh/uv) package manager
- Google Cloud Console project with Calendar API enabled

### Installation

1. **Install uv**:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Install Python 3.14**:
   ```bash
   uv python install 3.14
   ```

3. **Clone and setup**:
   ```bash
   git clone <your-repo-url>
   cd bulk-calendar-app
   uv sync
   ```

4. **Configure Google OAuth**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a project and enable Google Calendar API
   - Create OAuth 2.0 credentials (Desktop app)
   - Download `credentials.json` and place in project root
   - Add `http://localhost:5485/oauth2callback` to authorized redirect URIs

5. **Run the application**:
   ```bash
   uv run main.py
   ```

6. **First-time setup**:
   - Visit `http://localhost:5485`
   - Authenticate with Google when prompted
   - Go to Settings (gear icon) to configure your calendar aliases

## Usage

### Web Interface

1. **Create Events**:
   - Visit `http://localhost:5485`
   - Type events, one per line:
     ```
     @workout Push day Monday 7pm
     @work Team meeting Friday 2pm
     Dinner with Sarah at 7pm tomorrow
     ```
   - Events with `@alias` go to that calendar, others go to primary

2. **Configure Aliases**:
   - Click the settings gear icon
   - Add alias → calendar ID mappings
   - Click "View all my calendar IDs" to see available calendars

3. **Manage Aliases**:
   - Add multiple aliases dynamically
   - Use `primary` for your main calendar
   - Copy calendar IDs from the list view

### CLI Tool

Create individual events from command line:

```bash
# Using natural language
uv run cal-request.py --quick-add "Coffee with Alex tomorrow at 2pm"

# Using explicit fields
uv run cal-request.py --summary "Team Meeting" --start "2026-02-25T14:00:00" --end "2026-02-25T15:00:00"
```

### List All Calendars

```bash
uv run list_calendars.py
```

Shows all calendars with their IDs for alias configuration.

## Configuration

### Calendar Aliases

Aliases are stored in `calendar_aliases.json`:

```json
{
  "workout": "abc123@group.calendar.google.com",
  "work": "xyz789@group.calendar.google.com",
  "personal": "primary"
}
```

- Keys are the aliases you type (without `@`)
- Values are the actual Google Calendar IDs
- Use `primary` for your main calendar

### Environment Variables

- `FLASK_ENV`: Set to `production` to disable debug mode
- `SECRET_KEY`: Flask session secret (defaults to dev key)

## Project Structure

```
.
├── main.py                    # Flask web application
├── calendar_client.py         # Google Calendar API client
├── calendar_parser.py         # @alias text parser
├── cal-request.py            # CLI tool
├── list_calendars.py         # List all calendar IDs
├── quickstart.py             # OAuth setup helper
├── calendar_aliases.json     # User's alias configuration
├── templates/
│   ├── index.html           # Main event creation page
│   ├── settings.html        # Alias management page
│   └── calendars.html       # Calendar ID list view
├── pyproject.toml           # Project dependencies
├── Dockerfile               # Container configuration
└── docker-compose.yml       # Docker orchestration
```

## Development

#### Installation with Docker

1. **Build the Docker image**:
   ```bash
   docker compose build
   ```

2. **Configure Google OAuth**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a project and enable Google Calendar API
   - Create OAuth 2.0 credentials (Desktop app)
   - Download `credentials.json` and place in project root
   - Add `http://localhost:5485/oauth2callback` to authorized redirect URIs

3. **Start the container**:
   ```bash
   docker compose up
   ```

### Linting and Formatting

```bash
# Check code
uvx ruff check .

# Format code
uvx ruff format .
```

## How It Works

1. **Event Parsing**: When you submit events, `calendar_parser.py` extracts `@alias` prefixes using regex
2. **Alias Lookup**: The alias is looked up in `calendar_aliases.json` to get the real calendar ID
3. **API Call**: Google Calendar API's `quickAdd` endpoint parses the natural language and creates the event
4. **Error Handling**: Unknown aliases show error messages; API errors are caught and displayed

## Security Notes

- Never commit `credentials.json` or `token.json` (they're in .gitignore)
- `token.json` stores your OAuth tokens locally
- OAuth scope is limited to `https://www.googleapis.com/auth/calendar`
- Use environment variables for production secrets

## Troubleshooting

**"Unknown calendar alias" error**:
- Check your alias configuration in Settings
- Verify the alias exists in `calendar_aliases.json`

**Authentication errors**:
- Delete `token.json` to re-authenticate
- Ensure `credentials.json` is valid and not expired

**Events not appearing**:
- Check the correct calendar is selected in Google Calendar UI
- Verify the calendar ID in your alias configuration

