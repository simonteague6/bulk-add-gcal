"""Entry point for the Batch-Add-Events Flask application.

Run with:
    uv run run.py
    python run.py
"""

import os

from app import create_app

from dotenv import load_dotenv

load_dotenv()  # reads variables from a .env file and sets them in os.environ

app = create_app()

if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_ENV") != "production"
    app.run(debug=debug_mode, host="0.0.0.0", port=5485)
