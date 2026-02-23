#!/usr/bin/env python3
"""List all Google Calendar IDs available to the authenticated user."""

import calendar_client


def list_calendars(service):
    """Fetch and display all calendars with their IDs.

    Uses the Calendar API's calendarList endpoint to retrieve all calendars
    the user has access to, including primary and shared calendars.
    """
    page_token = None
    calendars = []

    while True:
        response = service.calendarList().list(pageToken=page_token).execute()
        calendars.extend(response.get("items", []))
        page_token = response.get("nextPageToken")

        if not page_token:
            break

    return calendars


def main():
    """Display all calendar IDs for the authenticated user."""
    try:
        service = calendar_client.build_service()
        calendars = list_calendars(service)

        print(f"\nFound {len(calendars)} calendar(s):\n")
        print("-" * 60)

        for cal in calendars:
            cal_id = cal.get("id", "N/A")
            summary = cal.get("summary", "Unnamed")
            primary = " (PRIMARY)" if cal.get("primary", False) else ""
            access = cal.get("accessRole", "unknown")

            print(f"Calendar: {summary}{primary}")
            print(f"ID:       {cal_id}")
            print(f"Access:   {access}")
            print("-" * 60)

    except Exception as error:
        print(f"Error fetching calendars: {error}")


if __name__ == "__main__":
    main()
