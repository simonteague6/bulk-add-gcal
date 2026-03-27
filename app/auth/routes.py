from flask import flash, redirect, url_for
from flask_login import login_required, logout_user

from app.auth import bp


@bp.route("/login")
def login():
    """Redirect to Google OAuth consent screen via Flask-Dance."""
    return redirect(url_for("google.login"))


@bp.route("/logout")
@login_required
def logout():
    """Clear the user's session."""
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login"))