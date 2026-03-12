import os
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Full access to Calendar. Required for creating/editing events.
SCOPES = ["https://www.googleapis.com/auth/calendar"]


def load_credentials():
    """Load OAuth credentials from token.json, or run the browser flow.

    How it works:
    - If token.json exists, we load saved access/refresh tokens.
    - If the access token is expired but refreshable, we refresh it.
    - Otherwise, we launch the installed-app OAuth flow which opens a browser.
    - After successful login, we save fresh tokens to token.json.
    """
    creds = None

    # token.json stores access/refresh tokens from a previous login.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # If no credentials or they're invalid, re-authenticate.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Refresh without user interaction.
            creds.refresh(Request())
        else:
            # Start browser-based OAuth flow for an installed app.
            # NOTE: This will be replaced with a proper web server OAuth flow
            # when Issue #5 (Replace Google Cloud Console setup) is implemented.
            flow = InstalledAppFlow.from_client_secrets_file(
                "data/credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Persist new tokens to disk for next run.
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds


def build_service():
    """Build and return an authenticated Google Calendar API v3 service."""
    return build("calendar", "v3", credentials=load_credentials())


def create_event_quick_add(service, calendar_id: str, text: str) -> dict:
    """Create an event using Google's natural language parsing (quickAdd).

    Args:
        service: Authenticated Google Calendar API service object.
        calendar_id: The calendar ID to create the event on.
        text: Natural language event description (e.g., "Team meeting Friday 2pm").

    Returns:
        The created event resource dict from the Google Calendar API.
    """
    return service.events().quickAdd(calendarId=calendar_id, text=text).execute()
