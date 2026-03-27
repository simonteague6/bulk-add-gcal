# app/models.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """A user who has signed in with Google.

    UserMixin provides the methods Flask-Login needs:
    is_authenticated, is_active, is_anonymous, get_id.
    """

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256), unique=True, nullable=False)
    name = db.Column(db.String(256))

    # Relationships — SQLAlchemy will auto-join these for you
    aliases = db.relationship("CalendarAlias", backref="user", lazy=True)


class OAuth(OAuthConsumerMixin, db.Model):
    """Stores OAuth tokens per user.

    OAuthConsumerMixin provides: provider, token (JSON), created_at.
    Flask-Dance reads/writes tokens through this table automatically.
    """

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User")


class CalendarAlias(db.Model):
    """A per-user mapping from alias name to Google Calendar ID.

    Replaces the old data/calendar_aliases.json file.
    """

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    alias = db.Column(db.String(64), nullable=False)
    calendar_id = db.Column(db.String(512), nullable=False)

    # A user can't have two aliases with the same name
    __table_args__ = (db.UniqueConstraint("user_id", "alias", name="uq_user_alias"),)
