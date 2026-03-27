"""Routes for the events blueprint: bulk event creation."""

from flask import flash, redirect, render_template, request, session, url_for
from flask_login import login_required, current_user
from flask_dance.contrib.google import google

from app.events import bp
from app.services import alias_parser, calendar_client


@bp.route("/")
@login_required
def index():
    """Render the main event creation page."""
    aliases = [a.alias for a in current_user.aliases]
    events = session.get("recent_events", [])
    return render_template("events/index.html", events=events, aliases=aliases)


@bp.route("/submit", methods=["POST"])
@login_required
def submit():
    """Accept bulk event text, parse each line, and create events via the Calendar API.

    Each line is parsed for an optional @alias prefix to route the event to the
    correct calendar. Events are stored in the session for display after redirect.
    """
    bulk_text = request.form.get("bulk-text")

    if not bulk_text:
        return redirect(url_for("events.index"))

    lines = [line.strip() for line in bulk_text.splitlines() if line.strip()]

    # Build per-user alias dict from the database
    user_aliases = {a.alias: a.calendar_id for a in current_user.aliases}

    # Ensure the user has a valid Google OAuth token before using the Calendar API
    if not google.authorized or not google.token:
        flash("Your Google connection has expired or is missing. Please reconnect and try again.", "error")
        return redirect(url_for("google.login"))
    # Build the Calendar API service from the current user's OAuth token
    service = calendar_client.build_service_for_user(google.token)

    created_events = []
    errors = []

    for line in lines:
        try:
            calendar_id, clean_text = alias_parser.parse_event_text(line, user_aliases)
            event = calendar_client.create_event_quick_add(
                service, calendar_id, clean_text
            )

            summary = event.get("summary", "NO SUMMARY")
            url = event.get("htmlLink", "NO URL")
            created_events.append({"summary": summary, "url": url})
        except ValueError as e:
            errors.append(str(e))
        except Exception as e:
            errors.append(f"Failed to create event: {str(e)}")

    for error in errors:
        flash(error, "error")

    MAX_RECENT_EVENTS = 50
    session["recent_events"] = created_events[-MAX_RECENT_EVENTS:]

    return redirect(url_for("events.index"))
