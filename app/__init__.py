"""Application factory for the Batch-Add-Events Flask app."""

import os

from flask import Flask


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

    # Register blueprints
    from app.events import bp as events_bp
    from app.settings import bp as settings_bp
    from app.auth import bp as auth_bp

    app.register_blueprint(events_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(auth_bp)

    return app
