"""Routes for the settings blueprint: calendar alias management."""

from flask import flash, redirect, render_template, request, url_for

from app.services import alias_parser, calendar_client
from app.services.list_calendars import list_calendars
from app.settings import bp


@bp.route("/settings", methods=["GET", "POST"])
def settings():
    """Manage calendar aliases.

    GET:  Render the settings page with existing alias mappings
          and available Google calendars.
    POST: Save updated alias-to-calendar-ID mappings from the form.
    """
    if request.method == "POST":
        aliases_data = request.form.getlist("alias[]")
        calendar_ids = request.form.getlist("calendar_id[]")

        aliases = {
            alias.strip().lower(): cal_id.strip()
            for alias, cal_id in zip(aliases_data, calendar_ids)
            if alias.strip() and cal_id.strip()
        }

        alias_parser.save_aliases(aliases)
        flash("Settings saved successfully!", "success")
        return redirect(url_for("settings.settings"))

    aliases = alias_parser.load_aliases()

    # Fetch calendars from Google API
    calendars = []
    try:
        service = calendar_client.build_service()
        calendars = list_calendars(service)
    except Exception as e:
        flash(f"Error fetching calendars: {e}", "error")

    # Build reverse mapping: calendar_id -> list of aliases
    aliases_by_calendar = {}
    for alias, cal_id in aliases.items():
        aliases_by_calendar.setdefault(cal_id, []).append(alias)

    return render_template(
        "settings/settings.html",
        aliases=aliases,
        calendars=calendars,
        aliases_by_calendar=aliases_by_calendar
    )


@bp.route("/list-calendars")
def list_calendars_view():
    """Redirect to the unified settings page.

    Previously displayed all Google calendars in a separate page.
    Now consolidated into the main settings interface.
    """
    return redirect(url_for("settings.settings"))
