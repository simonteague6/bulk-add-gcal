"""Routes for the auth blueprint.

Currently stubs only. Full implementation will be added in Issue #5:
"Replace Google Cloud Console setup with direct Google Signup/OAuth flow".

Planned routes:
- GET  /login           -- Redirect user to Google OAuth consent screen
- GET  /logout          -- Clear session and log user out
- GET  /oauth2callback  -- Handle redirect from Google after user grants access
"""

from flask import flash, redirect, url_for

from app.auth import bp


@bp.route("/login")
def login():
    """Stub: will initiate the Google OAuth web server flow (Issue #5)."""
    flash("Login is not yet implemented. Running in single-user mode.", "error")
    return redirect(url_for("events.index"))


@bp.route("/logout")
def logout():
    """Stub: will clear the user session and OAuth tokens (Issue #5)."""
    flash("Logout is not yet implemented.", "error")
    return redirect(url_for("events.index"))


@bp.route("/oauth2callback")
def oauth2callback():
    """Stub: will handle the OAuth redirect callback from Google (Issue #5)."""
    flash("OAuth callback is not yet implemented.", "error")
    return redirect(url_for("events.index"))
