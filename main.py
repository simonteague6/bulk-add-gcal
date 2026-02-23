import os
from flask import Flask, render_template, request, redirect, url_for, flash
import calendar_client
import calendar_parser

calendar_links = []
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")


@app.route("/")
def hello_world():
    aliases = calendar_parser.get_available_aliases()
    return render_template("index.html", events=calendar_links, aliases=aliases)


@app.route("/submit", methods=["POST"])
def handle_submit():
    global calendar_links
    bulk_text = request.form.get("bulk-text")

    if not bulk_text:
        return redirect(url_for("hello_world"))
    print(f"Received bulk text: {bulk_text}")
    lines = [l.strip() for l in bulk_text.splitlines() if l.strip()]
    service = calendar_client.build_service()

    calendar_links = []
    errors = []

    for line in lines:
        try:
            calendar_id, clean_text = calendar_parser.parse_event_text(line)
            event = (
                service.events()
                .quickAdd(calendarId=calendar_id, text=clean_text)
                .execute()
            )

            summary = event.get("summary", "NO SUMMARY")
            url = event.get("htmlLink", "NO URL")
            print(f"Title: {summary} URL: {url} Calendar: {calendar_id}")
            calendar_links.append({"summary": summary, "url": url})
        except ValueError as e:
            print(f"Error parsing line '{line}': {e}")
            errors.append(str(e))
        except Exception as e:
            print(f"Error creating event for '{line}': {e}")
            errors.append(f"Failed to create event: {str(e)}")

        if errors:
            for error in errors:
                flash(error, "error")

    return redirect(url_for("hello_world"))


@app.route("/settings", methods=["GET", "POST"])
def settings():
    """Manage calendar aliases."""
    if request.method == "POST":
        aliases = {}
        aliases_data = request.form.getlist("alias[]")
        calendar_ids = request.form.getlist("calendar_id[]")

        for alias, cal_id in zip(aliases_data, calendar_ids):
            if alias.strip() and cal_id.strip():
                aliases[alias.strip().lower()] = cal_id.strip()

        calendar_parser.save_aliases(aliases)
        flash("Settings saved successfully!", "success")
        return redirect(url_for("settings"))

    aliases = calendar_parser.load_aliases()
    return render_template("settings.html", aliases=aliases)


@app.route("/list-calendars")
def list_calendars():
    """Display all available calendar IDs."""
    try:
        service = calendar_client.build_service()
        page_token = None
        calendars = []

        while True:
            response = service.calendarList().list(pageToken=page_token).execute()
            calendars.extend(response.get("items", []))
            page_token = response.get("nextPageToken")
            if not page_token:
                break

        return render_template("calendars.html", calendars=calendars)
    except Exception as e:
        flash(f"Error fetching calendars: {e}", "error")
        return redirect(url_for("settings"))


if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_ENV") != "production"
    app.run(debug=debug_mode, host="0.0.0.0", port=5485)
