"""Routes for the settings blueprint: calendar alias management."""

from flask import flash, redirect, render_template, request, url_for
import re

from app.services import alias_parser, calendar_client
from app.services.list_calendars import list_calendars
from app.settings import bp


@bp.route("/settings", methods=["GET", "POST"])
def settings():
    """Manage calendar aliases.

    GET:  Render the settings page with calendars grouped by access role
          and alias fields for writable calendars.
    POST: Save updated alias-to-calendar-ID mappings from the form.
    """
    if request.method == "POST":
        aliases = {}
        invalid_aliases = []
        for key, value in request.form.items():
            if key.startswith("alias_for__") and value.strip():
                raw_value = value.strip()
                calendar_id = key[11:]  # Remove "alias_for__" prefix
                # Normalize alias: strip leading '@' if present and lowercase
                normalized = raw_value.lstrip("@").lower()
                # Validate alias to match what alias_parser.parse_event_text() can parse
                if re.fullmatch(r"\w+", normalized):
                    aliases[normalized] = calendar_id
                else:
                    invalid_aliases.append(raw_value)

        if invalid_aliases:
            # Inform the user that some aliases were not saved due to invalid characters
            flash(
                "These aliases were not saved because they contain invalid characters: "
                + ", ".join(sorted(set(invalid_aliases))),
                "error",
            )

        if aliases:
            alias_parser.save_aliases(aliases)
            flash(f"Aliases saved successfully! ({len(aliases)} aliases)", "success")
        elif not invalid_aliases:
            # No aliases provided at all
            pass
        return redirect(url_for("settings.settings"))

    aliases = alias_parser.load_aliases()

    # Fetch calendars from Google API
    calendars = []
    try:
        service = calendar_client.build_service()
        calendars = list_calendars(service)
    except Exception as e:
        flash(f"Error fetching calendars: {e}", "error")

    # Group calendars by access role
    writable_calendars = [
        c for c in calendars if c.get("accessRole") in ("owner", "writer")
    ]
    readonly_calendars = [
        c for c in calendars if c.get("accessRole") in ("reader", "freeBusyReader")
    ]

    # Sort writable calendars: primary first, then alphabetically by name
    writable_calendars.sort(
        key=lambda c: (0 if c.get("primary") else 1, c.get("summary", "").lower())
    )

    # Sort read-only calendars alphabetically by name
    readonly_calendars.sort(key=lambda c: c.get("summary", "").lower())

    # Build reverse mapping: calendar_id -> alias (for pre-filling fields)
    # Use the first alias found for each calendar ID
    alias_for_calendar = {}
    for alias, cal_id in aliases.items():
        if cal_id not in alias_for_calendar:
            alias_for_calendar[cal_id] = alias

    return render_template(
        "settings/settings.html",
        writable_calendars=writable_calendars,
        readonly_calendars=readonly_calendars,
        alias_for_calendar=alias_for_calendar,
    )


@bp.route("/list-calendars")
def list_calendars_view():
    """Redirect to the unified settings page.

    Previously displayed all Google calendars in a separate page.
    Now consolidated into the main settings interface.
    """
    return redirect(url_for("settings.settings"))
