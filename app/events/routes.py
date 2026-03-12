"""Routes for the events blueprint: bulk event creation."""

from flask import flash, redirect, render_template, request, session, url_for

from app.events import bp
from app.services import alias_parser, calendar_client


@bp.route("/")
def index():
    """Render the main event creation page."""
    aliases = alias_parser.get_available_aliases()
    events = session.get("recent_events", [])
    return render_template("events/index.html", events=events, aliases=aliases)


@bp.route("/submit", methods=["POST"])
def submit():
    """Accept bulk event text, parse each line, and create events via the Calendar API.

    Each line is parsed for an optional @alias prefix to route the event to the
    correct calendar. Events are stored in the session for display after redirect.
    """
    bulk_text = request.form.get("bulk-text")

    if not bulk_text:
        return redirect(url_for("events.index"))

    lines = [line.strip() for line in bulk_text.splitlines() if line.strip()]
    service = calendar_client.build_service()

    created_events = []
    errors = []

    for line in lines:
        try:
            calendar_id, clean_text = alias_parser.parse_event_text(line)
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

    # Flash all errors once after processing all lines (not inside the loop).
    for error in errors:
        flash(error, "error")

    # Store created events in the session so they survive the redirect.
    session["recent_events"] = created_events

    return redirect(url_for("events.index"))
