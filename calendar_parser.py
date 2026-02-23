"""Parse event text to extract calendar aliases and route to correct calendar."""

import json
import re


def load_aliases(config_path: str = "calendar_aliases.json") -> dict:
    """Load calendar aliases from JSON config file.

    Returns a dict mapping alias names to calendar IDs.
    """
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {config_path}: {e}")


def save_aliases(aliases: dict, config_path: str = "calendar_aliases.json") -> None:
    """Save calendar aliases to JSON config file."""
    with open(config_path, "w") as f:
        json.dump(aliases, f, indent=2)


def parse_event_text(text: str, aliases: dict | None = None) -> tuple[str, str]:
    """Parse event text to extract @alias and return (calendar_id, clean_text).

    Args:
        text: Event text potentially containing @alias (e.g., "@workout Push day")
        aliases: Dict mapping alias names to calendar IDs. Loads from file if None.

    Returns:
        Tuple of (calendar_id, clean_text_without_alias)

    Raises:
        ValueError: If alias is not found in the mapping
    """
    if aliases is None:
        aliases = load_aliases()

    # Match @alias at the start of the text
    match = re.match(r"@(\w+)\s+(.*)", text.strip())

    if not match:
        # No alias found, use primary calendar
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


def get_available_aliases(config_path: str = "calendar_aliases.json") -> list[str]:
    """Return list of available alias names."""
    aliases = load_aliases(config_path)
    return list(aliases.keys())
