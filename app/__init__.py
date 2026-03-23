"""Application factory for the Batch-Add-Events Flask app."""

import os

from flask import Flask
from app.models import db


def create_app() -> Flask:
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
    db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "data", "app.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"

    # Initialize SQLAlchemy with this app
    db.init_app(app)

    # Create tables if they don't exist yet
    with app.app_context():
        db.create_all()


    # Register blueprints
    from app.events import bp as events_bp
    from app.settings import bp as settings_bp
    from app.auth import bp as auth_bp

    app.register_blueprint(events_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(auth_bp)

    return app
