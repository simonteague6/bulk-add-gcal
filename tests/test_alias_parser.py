import pytest

from app.services import alias_parser


class TestLoadAliases:
    def test_returns_user_aliases(self, user, user_aliases):
        result = alias_parser.load_aliases(user.id)
        assert result == {"work": "work@example.com", "personal": "personal@example.com"}

    def test_empty_when_no_aliases(self, user):
        result = alias_parser.load_aliases(user.id)
        assert result == {}

    def test_only_returns_current_user(self, user, second_user):
        from app.models import db, CalendarAlias

        db.session.add(
            CalendarAlias(user_id=user.id, alias="mine", calendar_id="mine@example.com")
        )
        db.session.add(
            CalendarAlias(
                user_id=second_user.id,
                alias="theirs",
                calendar_id="theirs@example.com",
            )
        )
        db.session.commit()

        result = alias_parser.load_aliases(user.id)
        assert result == {"mine": "mine@example.com"}
        assert "theirs" not in result


class TestSaveAliases:
    def test_creates_db_rows(self, user):
        from app.models import CalendarAlias

        alias_parser.save_aliases({"work": "work@example.com"}, user.id)

        rows = CalendarAlias.query.filter_by(user_id=user.id).all()
        assert len(rows) == 1
        assert rows[0].alias == "work"
        assert rows[0].calendar_id == "work@example.com"

    def test_replaces_existing(self, user, user_aliases):
        from app.models import CalendarAlias

        alias_parser.save_aliases({"new": "new@example.com"}, user.id)

        rows = CalendarAlias.query.filter_by(user_id=user.id).all()
        assert len(rows) == 1
        assert rows[0].alias == "new"

    def test_empty_dict_clears(self, user, user_aliases):
        from app.models import CalendarAlias

        alias_parser.save_aliases({}, user.id)

        rows = CalendarAlias.query.filter_by(user_id=user.id).all()
        assert len(rows) == 0


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
    def test_returns_names(self, user, user_aliases):
        result = alias_parser.get_available_aliases(user.id)
        assert set(result) == {"work", "personal"}

    def test_empty(self, user):
        result = alias_parser.get_available_aliases(user.id)
        assert result == []
