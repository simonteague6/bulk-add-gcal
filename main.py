import os
from flask import Flask, render_template, request, redirect, url_for
import calendar_client

calendar_links = []
app = Flask(__name__)


@app.route("/")
def hello_world():
    print(f"events: {calendar_links}")
    return render_template("index.html", events=calendar_links)


@app.route("/submit", methods=["POST"])
def handle_submit():
    global calendar_links
    bulk_text = request.form.get("bulk-text")
    audio_file = request.files.get("audio-upload")

    if bulk_text:
        print(f"Received bulk text: {bulk_text}")
        lines = [l.strip() for l in bulk_text.splitlines() if l.strip()]
        service = calendar_client.build_service()
        created = calendar_client.create_many_quick_add_events(service, lines)

        calendar_links = []
        for event in created:
            summary = event.get("summary", "NO SUMMARY")
            url = event.get("htmlLink", "NO URL")
            print(f"Title: {summary} URL: {url}")

            calendar_links.append({"summary": summary, "url": url})

    if audio_file:
        print(f"Audio file uploaded: {audio_file.filename}")
        # Save the file if needed:
        # audio_file.save(f"uploads/{audio_file.filename}")

    # Redirect back to home or show success page
    return redirect(url_for("hello_world"))


if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_ENV") != "production"
    app.run(debug=debug_mode, host="0.0.0.0", port=5485)
