"""Routes for the settings blueprint: calendar alias management."""

import re

from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required, current_user
from flask_dance.contrib.google import google

from app.models import db, CalendarAlias
from app.services import calendar_client
from app.services.list_calendars import list_calendars
from app.settings import bp


@bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    """Manage calendar aliases.

    GET:  Render the settings page with calendars grouped by access role
          and alias fields for writable calendars.
    POST: Save updated alias-to-calendar-ID mappings for the current user.
    """
    if request.method == "POST":
        has_alias_fields = any(
            key.startswith("alias_for__") for key in request.form.keys()
        )
        if not has_alias_fields:
            flash(
                "No calendar aliases were submitted; existing aliases were not changed.",
                "error",
            )
            return redirect(url_for("settings.settings"))

        aliases = {}
        invalid_aliases = []
        for key, value in request.form.items():
            if key.startswith("alias_for__") and value.strip():
                raw_value = value.strip()
                calendar_id = key[11:]  # Remove "alias_for__" prefix
                normalized = raw_value.lstrip("@").lower()
                if re.fullmatch(r"\w+", normalized):
                    aliases[normalized] = calendar_id
                else:
                    invalid_aliases.append(raw_value)

        if invalid_aliases:
            flash(
                "These aliases were not saved because they contain invalid characters: "
                + ", ".join(sorted(set(invalid_aliases))),
                "error",
            )

        if aliases:
            # Delete this user's existing aliases, then insert the new set
            CalendarAlias.query.filter_by(user_id=current_user.id).delete()
            for alias_name, cal_id in aliases.items():
                db.session.add(CalendarAlias(
                    user_id=current_user.id,
                    alias=alias_name,
                    calendar_id=cal_id,
                ))
            db.session.commit()
            flash(f"Aliases saved successfully! ({len(aliases)} aliases)", "success")

        return redirect(url_for("settings.settings"))

    # Build per-user alias reverse map: calendar_id -> alias (for pre-filling form fields)
    alias_for_calendar = {}
    for row in current_user.aliases:
        if row.calendar_id not in alias_for_calendar:
            alias_for_calendar[row.calendar_id] = row.alias

    # Fetch the user's calendars from Google
    calendars = []
    try:
        service = calendar_client.build_service_for_user(google.token)
        calendars = list_calendars(service)
    except Exception as e:
        flash(f"Error fetching calendars: {e}", "error")

    writable_calendars = [
        c for c in calendars if c.get("accessRole") in ("owner", "writer")
    ]
    readonly_calendars = [
        c for c in calendars if c.get("accessRole") in ("reader", "freeBusyReader")
    ]

    writable_calendars.sort(
        key=lambda c: (0 if c.get("primary") else 1, c.get("summary", "").lower())
    )
    readonly_calendars.sort(key=lambda c: c.get("summary", "").lower())

    return render_template(
        "settings/settings.html",
        writable_calendars=writable_calendars,
        readonly_calendars=readonly_calendars,
        alias_for_calendar=alias_for_calendar,
    )
