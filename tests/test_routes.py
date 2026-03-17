import pytest


class TestEventsRoutes:
    def test_index_renders_template(self, client):
        response = client.get("/")

        assert response.status_code == 200
        assert b"Bulk Add Events" in response.data or b"events" in response.data

    def test_index_shows_recent_events_from_session(self, client):
        with client.session_transaction() as session:
            session["recent_events"] = [
                {"summary": "Test Event 1", "url": "https://example.com/1"},
                {"summary": "Test Event 2", "url": "https://example.com/2"},
            ]

        response = client.get("/")

        assert response.status_code == 200

    def test_submit_empty_text_redirects(self, client):
        response = client.post("/submit", data={"bulk-text": ""})

        assert response.status_code == 302
        assert response.headers["Location"] == "/"

    def test_submit_no_data_redirects(self, client):
        response = client.post("/submit", data={})

        assert response.status_code == 302
        assert response.headers["Location"] == "/"

    def test_submit_creates_events(self, client, mocker, mock_aliases_file):
        mock_service = mocker.MagicMock()
        mock_events = mocker.MagicMock()
        mock_service.events.return_value = mock_events

        mock_events.quickAdd.return_value.execute.side_effect = [
            {"summary": "Event 1", "htmlLink": "https://calendar.google.com/1"},
            {"summary": "Event 2", "htmlLink": "https://calendar.google.com/2"},
        ]

        mocker.patch(
            "app.services.calendar_client.build_service", return_value=mock_service
        )
        mocker.patch(
            "app.services.alias_parser.load_aliases",
            return_value={"work": "work@example.com"},
        )

        response = client.post(
            "/submit",
            data={"bulk-text": "Meeting tomorrow\n@work Project review"},
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert mock_events.quickAdd.call_count == 2

    def test_submit_handles_alias_error(self, client, mocker, mock_aliases_file):
        mock_service = mocker.MagicMock()
        mocker.patch(
            "app.services.calendar_client.build_service", return_value=mock_service
        )
        mocker.patch(
            "app.services.alias_parser.load_aliases",
            return_value={"work": "work@example.com"},
        )

        response = client.post(
            "/submit",
            data={"bulk-text": "@unknown_alias Some event"},
            follow_redirects=True,
        )

        assert response.status_code == 200

    def test_submit_limits_recent_events(self, client, mocker):
        mock_service = mocker.MagicMock()
        mock_events = mocker.MagicMock()
        mock_service.events.return_value = mock_events

        mock_events.quickAdd.return_value.execute.return_value = {
            "summary": "Event",
            "htmlLink": "https://example.com",
        }

        mocker.patch(
            "app.services.calendar_client.build_service", return_value=mock_service
        )
        mocker.patch("app.services.alias_parser.load_aliases", return_value={})

        events_text = "\n".join([f"Event {i}" for i in range(60)])

        client.post(
            "/submit",
            data={"bulk-text": events_text},
            follow_redirects=True,
        )

        with client.session_transaction() as session:
            assert len(session["recent_events"]) == 50


class TestSettingsRoutes:
    def test_settings_renders_template(
        self, client, mock_calendar_service, sample_calendars
    ):
        mock_calendar_list = mock_calendar_service.calendarList.return_value
        mock_calendar_list.list.return_value.execute.return_value = {
            "items": sample_calendars
        }

        response = client.get("/settings")

        assert response.status_code == 200

    def test_settings_groups_calendars_by_access(
        self, client, mock_calendar_service, sample_calendars
    ):
        mock_calendar_list = mock_calendar_service.calendarList.return_value
        mock_calendar_list.list.return_value.execute.return_value = {
            "items": sample_calendars
        }

        response = client.get("/settings")

        assert response.status_code == 200

    def test_settings_shows_existing_aliases(
        self, client, mock_calendar_service, sample_calendars, mocker
    ):
        mocker.patch(
            "app.services.alias_parser.load_aliases",
            return_value={"work": "work@example.com"},
        )

        mock_calendar_list = mock_calendar_service.calendarList.return_value
        mock_calendar_list.list.return_value.execute.return_value = {
            "items": sample_calendars
        }

        response = client.get("/settings")

        assert response.status_code == 200

    def test_settings_post_saves_aliases(
        self, client, mock_calendar_service, sample_calendars, mocker, tmp_path
    ):
        mock_save = mocker.patch("app.services.alias_parser.save_aliases")

        mock_calendar_list = mock_calendar_service.calendarList.return_value
        mock_calendar_list.list.return_value.execute.return_value = {
            "items": sample_calendars
        }

        response = client.post(
            "/settings",
            data={
                "alias_for__work@example.com": "work",
                "alias_for__personal@example.com": "personal",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        mock_save.assert_called_once()

    def test_settings_post_validates_alias_format(
        self, client, mock_calendar_service, sample_calendars, mocker
    ):
        mock_save = mocker.patch("app.services.alias_parser.save_aliases")

        mock_calendar_list = mock_calendar_service.calendarList.return_value
        mock_calendar_list.list.return_value.execute.return_value = {
            "items": sample_calendars
        }

        response = client.post(
            "/settings",
            data={
                "alias_for__work@example.com": "valid-alias",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        mock_save.assert_not_called()

    def test_settings_post_normalizes_alias(
        self, client, mock_calendar_service, sample_calendars, mocker
    ):
        mock_save = mocker.patch("app.services.alias_parser.save_aliases")

        mock_calendar_list = mock_calendar_service.calendarList.return_value
        mock_calendar_list.list.return_value.execute.return_value = {
            "items": sample_calendars
        }

        response = client.post(
            "/settings",
            data={
                "alias_for__work@example.com": "@Work",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        called_aliases = mock_save.call_args[0][0]
        assert "work" in called_aliases

    def test_settings_post_empty_aliases(
        self, client, mock_calendar_service, sample_calendars, mocker
    ):
        mock_save = mocker.patch("app.services.alias_parser.save_aliases")

        mock_calendar_list = mock_calendar_service.calendarList.return_value
        mock_calendar_list.list.return_value.execute.return_value = {
            "items": sample_calendars
        }

        response = client.post(
            "/settings",
            data={
                "alias_for__work@example.com": "",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        mock_save.assert_not_called()

    def test_settings_handles_api_error(self, client, mocker):
        mocker.patch(
            "app.services.calendar_client.build_service",
            side_effect=Exception("API Error"),
        )

        response = client.get("/settings")

        assert response.status_code == 200

    def test_list_calendars_redirects_to_settings(self, client):
        response = client.get("/list-calendars")

        assert response.status_code == 302
        assert "/settings" in response.headers["Location"]


class TestAuthRoutes:
    def test_auth_login_redirects(self, client):
        response = client.get("/login")

        assert response.status_code == 302

    def test_auth_callback(self, client):
        response = client.get("/oauth2callback")

        assert response.status_code == 302

    def test_auth_logout(self, client):
        response = client.get("/logout")

        assert response.status_code == 302
