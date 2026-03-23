import os
from flask import Blueprint, flash, redirect, url_for
from flask_dance.contrib.google import make_google_blueprint
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from flask_dance.consumer import oauth_authorized
from flask_login import current_user, login_user

from app.models import db, OAuth, User

bp = Blueprint("auth", __name__, template_folder="templates")

google_bp = make_google_blueprint(
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    scope=[
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/calendar",
    ],
    storage=SQLAlchemyStorage(OAuth, db.session, user=current_user),
    redirect_url="/",  # Where to go after successful login
)

# Flask-Dance's blueprint handles /login/google and /login/google/authorized
# We prefix it so the routes become /login/google and /login/google/authorized
bp_prefix = "/login"

@oauth_authorized.connect_via(google_bp)
def google_logged_in(blueprint, token):
    """Called after Google OAuth succeeds. Creates user if needed, logs them in."""
    if not token:
        flash("Failed to sign in with Google.", "error")
        return False

    # Use the token to fetch user info from Google
    resp = blueprint.session.get("/oauth2/v1/userinfo")
    if not resp.ok:
        flash("Failed to fetch user info from Google.", "error")
        return False

    info = resp.json()
    email = info.get("email")
    name = info.get("name", "")

    # Find or create the user
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(email=email, name=name)
        db.session.add(user)
        db.session.commit()

    # Log the user in (sets the session cookie)
    login_user(user)

    # Return False to tell Flask-Dance we handled token storage ourselves
    # (it will still store the token via SQLAlchemyStorage)
    return False

from app.auth import routes  # noqa: E402, F401