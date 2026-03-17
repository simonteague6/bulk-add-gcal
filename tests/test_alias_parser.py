import json

import pytest

from app.services import alias_parser


class TestLoadAliases:
    def test_load_aliases_existing_file(self, tmp_path):
        aliases_data = {"work": "work@example.com", "personal": "personal@example.com"}
        aliases_file = tmp_path / "aliases.json"
        aliases_file.write_text(json.dumps(aliases_data))

        result = alias_parser.load_aliases(str(aliases_file))

        assert result == aliases_data

    def test_load_aliases_missing_file(self, tmp_path):
        result = alias_parser.load_aliases(str(tmp_path / "nonexistent.json"))

        assert result == {}

    def test_load_aliases_invalid_json(self, tmp_path):
        aliases_file = tmp_path / "invalid.json"
        aliases_file.write_text("not valid json")

        with pytest.raises(ValueError, match="Invalid JSON"):
            alias_parser.load_aliases(str(aliases_file))


class TestSaveAliases:
    def test_save_aliases_creates_file(self, tmp_path):
        aliases_data = {"work": "work@example.com"}
        aliases_file = tmp_path / "aliases.json"

        alias_parser.save_aliases(aliases_data, str(aliases_file))

        assert aliases_file.exists()
        with open(aliases_file) as f:
            assert json.load(f) == aliases_data

    def test_save_aliases_overwrites_existing(self, tmp_path):
        aliases_file = tmp_path / "aliases.json"
        aliases_file.write_text(json.dumps({"old": "old@example.com"}))

        new_data = {"new": "new@example.com"}
        alias_parser.save_aliases(new_data, str(aliases_file))

        with open(aliases_file) as f:
            assert json.load(f) == new_data

    def test_save_aliases_empty_dict(self, tmp_path):
        aliases_file = tmp_path / "aliases.json"
        aliases_file.write_text(json.dumps({"existing": "data@example.com"}))

        alias_parser.save_aliases({}, str(aliases_file))

        with open(aliases_file) as f:
            assert json.load(f) == {}


class TestParseEventText:
    def test_parse_with_valid_alias(self):
        aliases = {"work": "work@example.com"}

        calendar_id, clean_text = alias_parser.parse_event_text(
            "@work Meeting at 3pm", aliases
        )

        assert calendar_id == "work@example.com"
        assert clean_text == "Meeting at 3pm"

    def test_parse_with_alias_lowercase(self):
        aliases = {"work": "work@example.com"}

        calendar_id, clean_text = alias_parser.parse_event_text(
            "@WORK Meeting", aliases
        )

        assert calendar_id == "work@example.com"
        assert clean_text == "Meeting"

    def test_parse_without_alias_returns_primary(self):
        aliases = {"work": "work@example.com"}

        calendar_id, clean_text = alias_parser.parse_event_text(
            "Just a regular event", aliases
        )

        assert calendar_id == "primary"
        assert clean_text == "Just a regular event"

    def test_parse_empty_text(self):
        aliases = {"work": "work@example.com"}

        calendar_id, clean_text = alias_parser.parse_event_text("", aliases)

        assert calendar_id == "primary"
        assert clean_text == ""

    def test_parse_whitespace_only_text(self):
        aliases = {"work": "work@example.com"}

        calendar_id, clean_text = alias_parser.parse_event_text("   ", aliases)

        assert calendar_id == "primary"
        assert clean_text == ""

    def test_parse_unknown_alias_raises_error(self):
        aliases = {"work": "work@example.com"}

        with pytest.raises(ValueError, match="Unknown calendar alias '@unknown'"):
            alias_parser.parse_event_text("@unknown Some event", aliases)

    def test_parse_alias_without_text_not_matched(self):
        aliases = {"work": "work@example.com"}

        calendar_id, clean_text = alias_parser.parse_event_text("@work", aliases)

        assert calendar_id == "primary"
        assert clean_text == "@work"

    def test_parse_alias_with_multiple_spaces(self):
        aliases = {"work": "work@example.com"}

        calendar_id, clean_text = alias_parser.parse_event_text(
            "@work    Meeting", aliases
        )

        assert calendar_id == "work@example.com"
        assert clean_text == "Meeting"

    def test_parse_alias_leading_spaces(self):
        aliases = {"work": "work@example.com"}

        calendar_id, clean_text = alias_parser.parse_event_text(
            "   @work Meeting", aliases
        )

        assert calendar_id == "work@example.com"
        assert clean_text == "Meeting"

    def test_parse_alias_mid_text_not_recognized(self):
        aliases = {"work": "work@example.com"}

        calendar_id, clean_text = alias_parser.parse_event_text(
            "Event @work Meeting", aliases
        )

        assert calendar_id == "primary"
        assert clean_text == "Event @work Meeting"


class TestGetAvailableAliases:
    def test_get_available_aliases(self, tmp_path, monkeypatch):
        aliases_data = {"work": "work@example.com", "personal": "personal@example.com"}
        aliases_file = tmp_path / "aliases.json"
        aliases_file.write_text(json.dumps(aliases_data))

        result = alias_parser.get_available_aliases(str(aliases_file))

        assert set(result) == {"work", "personal"}

    def test_get_available_aliases_empty(self, tmp_path):
        result = alias_parser.get_available_aliases(str(tmp_path / "nonexistent.json"))

        assert result == []
