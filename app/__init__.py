"""Application factory for the Batch-Add-Events Flask app."""

import os

from flask import Flask
from app.models import db
from flask_login import LoginManager

# Allow OAuth over HTTP only when explicitly enabled. oauthlib enforces HTTPS
# by default, which breaks localhost. For local development or testing, set
# ALLOW_INSECURE_OAUTH_TRANSPORT=1. Do not set this in production.
if os.getenv("ALLOW_INSECURE_OAUTH_TRANSPORT") == "1":
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


def create_app(test_config: dict | None = None) -> Flask:
    """Create and configure the Flask application.

    Uses the application factory pattern so the app can be created with
    different configurations (e.g., testing vs. production) and to avoid
    circular imports between blueprints.

    Returns:
        Configured Flask application instance.
    """
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")

    # Database config — SQLite file in data/ directory
    db_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "..", "data", "app.db"
    )
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"

    if test_config:
        app.config.update(test_config)

    # Initialize SQLAlchemy with this app
    db.init_app(app)

    # Set up Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"

    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        """Flask-Login calls this on every request to load the user from the
        session cookie's stored user_id."""
        from app.models import User

        return User.query.get(int(user_id))

    # Create tables if they don't exist yet
    with app.app_context():
        db.create_all()

    # Register blueprints
    from app.events import bp as events_bp
    from app.settings import bp as settings_bp
    from app.auth import bp as auth_bp, google_bp


    app.register_blueprint(events_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(google_bp, url_prefix="/login")

    return app
