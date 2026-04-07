import os

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/calendar.calendarlist.readonly",
]


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
    # Validate token structure before attempting to build credentials.
    if not isinstance(token, dict) or not token.get("access_token"):
        # This indicates the user is not properly authenticated and should
        # be redirected through the OAuth flow again by the caller.
        raise ValueError(
            "Missing or invalid OAuth token; user re-authentication required."
        )

    # Validate that required Google OAuth client configuration is present.
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    if not client_id or not client_secret:
        # This is a server-side configuration error rather than a user issue.
        raise RuntimeError(
            "Google OAuth client_id/client_secret not configured in environment."
        )

    creds = Credentials(
        token=token["access_token"],
        refresh_token=token.get("refresh_token"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
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
