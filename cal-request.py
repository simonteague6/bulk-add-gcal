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
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Persist new tokens to disk for next run.
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds


def parse_args():
    """Parse command-line arguments.

    This keeps CLI parsing separate from the API logic so the code is reusable.
    """
    parser = argparse.ArgumentParser(
        description="Create a Google Calendar event on the primary calendar."
    )
    parser.add_argument("--summary", default="Test Event", help="Event title")
    parser.add_argument("--location", default="", help="Event location")
    parser.add_argument("--description", default="", help="Event description")
    parser.add_argument(
        "--start",
        default="",
        help=(
            "Start time ISO-8601 (e.g. 2026-02-10T10:00:00-05:00). "
            "Defaults to now+10m."
        ),
    )
    parser.add_argument(
        "--end",
        default="",
        help=(
            "End time ISO-8601 (e.g. 2026-02-10T11:00:00-05:00). "
            "Defaults to start+1h."
        ),
    )
    parser.add_argument(
        "--quick-add",
        default="",
        help=(
            "Natural language event text (e.g. 'Coffee with Alex tomorrow at 2pm'). "
            "If provided, uses the Calendar quickAdd endpoint instead of manual fields."
        ),
    )
    return parser.parse_args()


def compute_times(start_arg: str, end_arg: str):
    """Compute start/end datetimes.

    - If start is provided, parse it.
    - Otherwise default to now + 10 minutes.
    - If end is provided, parse it.
    - Otherwise default to start + 1 hour.
    """
    if start_arg:
        start_dt = dt.datetime.fromisoformat(start_arg)
    else:
        start_dt = dt.datetime.now().astimezone() + dt.timedelta(minutes=10)

    if end_arg:
        end_dt = dt.datetime.fromisoformat(end_arg)
    else:
        end_dt = start_dt + dt.timedelta(hours=1)

    return start_dt, end_dt


def create_event_manual(service, args):
    """Create an event using explicit fields like summary, start, and end."""
    start_dt, end_dt = compute_times(args.start, args.end)

    # Event body sent to the API. This is a Python dict that becomes JSON.
    event = {
        "summary": args.summary,
        "location": args.location,
        "description": args.description,
        "start": {"dateTime": start_dt.isoformat()},
        "end": {"dateTime": end_dt.isoformat()},
    }

    return service.events().insert(calendarId="primary", body=event).execute()


def create_event_quick_add(service, text: str):
    """Create an event using Google's natural language parsing (quickAdd)."""
    return (
        service.events()
        .quickAdd(calendarId="primary", text=text)
        .execute()
    )


def main():
    """Create an event on the primary Google Calendar."""
    args = parse_args()

    try:
        # Build the Google Calendar API client.
        service = build("calendar", "v3", credentials=load_credentials())

        if args.quick_add:
            created = create_event_quick_add(service, args.quick_add)
        else:
            created = create_event_manual(service, args)

        print(f"Event created: {created.get('htmlLink')}")
    except HttpError as error:
        # HttpError covers API errors like invalid auth or bad request body.
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    main()
