import argparse
import datetime as dt
import os
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

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
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        # Persist new tokens to disk for next run.
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds


def build_service():
    service = build("calendar", "v3", credentials=load_credentials())
    return service


def create_event_quick_add(service, text: str):
    """Create an event using Google's natural language parsing (quickAdd)."""
    return service.events().quickAdd(calendarId="primary", text=text).execute()


def create_many_quick_add_events(service, eventList: list):
    """Create an event using Google's natural language parsing (quickAdd)."""
    results = []
    for event in eventList:
        serviceOutput = (
            service.events().quickAdd(calendarId="primary", text=event).execute()
        )
        results.append(serviceOutput)
    return results
