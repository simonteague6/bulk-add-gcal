import os

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar"]


def build_service_for_user(token: dict) -> object:
    """Build an authenticated Google Calendar API service from a Flask-Dance token.

    Flask-Dance stores OAuth tokens as dicts with keys like 'access_token',
    'refresh_token', 'token_type', 'expires_in', etc. This function converts
    that dict into a google-auth Credentials object and builds the API service.

    Args:
        token: The OAuth token dict retrieved from Flask-Dance (google.token).

    Returns:
        Authenticated Google Calendar API v3 service object.
    """
    creds = Credentials(
        token=token["access_token"],
        refresh_token=token.get("refresh_token"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        scopes=SCOPES,
    )
    return build("calendar", "v3", credentials=creds)


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
