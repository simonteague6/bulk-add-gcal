"""Parse event text to extract calendar aliases and route to the correct calendar."""

import re
from app.models import CalendarAlias, db
from flask_login import current_user


def load_aliases() -> dict:
    """Load calendar aliases from CalendarAlias table for the current user.

    Returns a dict mapping alias names to calendar IDs.
    Returns an empty dict if no aliases are configured.
    """
    aliases = {}
    for a in CalendarAlias.query.filter_by(user_id=current_user.id).all():
        aliases[a.alias] = a.calendar_id
    return aliases



def save_aliases(aliases: dict) -> None:
    """Save calendar aliases to database for the current user."""
    # Delete existing aliases
    CalendarAlias.query.filter_by(user_id=current_user.id).delete()
    # Add new aliases
    for alias, calendar_id in aliases.items():
        new_alias = CalendarAlias(user_id=current_user.id, alias=alias, calendar_id=calendar_id)
        db.session.add(new_alias)
    db.session.commit()




def parse_event_text(text: str, aliases: dict | None = None) -> tuple[str, str]:
    """Parse event text to extract @alias and return (calendar_id, clean_text).

    Args:
        text: Event text potentially containing @alias (e.g., "@workout Push day")
        aliases: Dict mapping alias names to calendar IDs. Loads from file if None.

    Returns:
        Tuple of (calendar_id, clean_text_without_alias)

    Raises:
        ValueError: If the alias prefix is present but not found in the mapping.
    """
    if aliases is None:
        aliases = load_aliases()

    # Match @alias at the start of the text
    match = re.match(r"@(\w+)\s+(.*)", text.strip())

    if not match:
        # No alias found -- default to the primary calendar.
        return ("primary", text.strip())

    alias = match.group(1).lower()
    clean_text = match.group(2).strip()

    if alias not in aliases:
        available = ", ".join(f"@{k}" for k in aliases.keys())
        raise ValueError(
            f"Unknown calendar alias '@{alias}'. "
            f"Available aliases: {available or 'none configured'}"
        )

    calendar_id = aliases[alias]
    return (calendar_id, clean_text)


def get_available_aliases() -> list[str]:
    """Return list of available alias names."""
    aliases = load_aliases()
    return list(aliases.keys())
