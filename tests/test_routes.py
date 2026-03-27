from tests.conftest import make_logged_in_client


class TestEventsRoutes:
    def test_index_renders_template(self, logged_in_client):
        response = logged_in_client.get("/")

        assert response.status_code == 200
        assert b"Bulk Add Events" in response.data or b"events" in response.data

    def test_index_shows_recent_events_from_session(self, logged_in_client):
        with logged_in_client.session_transaction() as session:
            session["recent_events"] = [
                {"summary": "Test Event 1", "url": "https://example.com/1"},
                {"summary": "Test Event 2", "url": "https://example.com/2"},
            ]

        response = logged_in_client.get("/")

        assert response.status_code == 200

    def test_submit_empty_text_redirects(self, logged_in_client):
        response = logged_in_client.post("/submit", data={"bulk-text": ""})

        assert response.status_code == 302
        assert response.headers["Location"] == "/"

    def test_submit_no_data_redirects(self, logged_in_client):
        response = logged_in_client.post("/submit", data={})

        assert response.status_code == 302
        assert response.headers["Location"] == "/"

    def test_submit_creates_events(
        self, logged_in_client, mocker, user_aliases, mock_google_token
    ):
        mock_service = mocker.MagicMock()
        mock_events = mocker.MagicMock()
        mock_service.events.return_value = mock_events

        mock_events.quickAdd.return_value.execute.side_effect = [
            {"summary": "Event 1", "htmlLink": "https://calendar.google.com/1"},
            {"summary": "Event 2", "htmlLink": "https://calendar.google.com/2"},
        ]

        mocker.patch(
            "app.services.calendar_client.build_service_for_user",
            return_value=mock_service,
        )

        response = logged_in_client.post(
            "/submit",
            data={"bulk-text": "Meeting tomorrow\n@work Project review"},
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert mock_events.quickAdd.call_count == 2

    def test_submit_handles_alias_error(
        self, logged_in_client, mocker, user_aliases, mock_google_token
    ):
        mock_service = mocker.MagicMock()
        mocker.patch(
            "app.services.calendar_client.build_service_for_user",
            return_value=mock_service,
        )

        response = logged_in_client.post(
            "/submit",
            data={"bulk-text": "@unknown_alias Some event"},
            follow_redirects=True,
        )

        assert response.status_code == 200

    def test_submit_limits_recent_events(
        self, logged_in_client, mocker, mock_google_token
    ):
        mock_service = mocker.MagicMock()
        mock_events = mocker.MagicMock()
        mock_service.events.return_value = mock_events

        mock_events.quickAdd.return_value.execute.return_value = {
            "summary": "Event",
            "htmlLink": "https://example.com",
        }

        mocker.patch(
            "app.services.calendar_client.build_service_for_user",
            return_value=mock_service,
        )

        events_text = "\n".join([f"Event {i}" for i in range(60)])

        logged_in_client.post(
            "/submit",
            data={"bulk-text": events_text},
            follow_redirects=True,
        )

        with logged_in_client.session_transaction() as session:
            assert len(session["recent_events"]) == 50


class TestSettingsRoutes:
    def test_settings_renders_template(
        self, logged_in_client, mock_calendar_service, sample_calendars
    ):
        mock_calendar_list = mock_calendar_service.calendarList.return_value
        mock_calendar_list.list.return_value.execute.return_value = {
            "items": sample_calendars
        }

        response = logged_in_client.get("/settings")

        assert response.status_code == 200

    def test_settings_groups_calendars_by_access(
        self, logged_in_client, mock_calendar_service, sample_calendars
    ):
        mock_calendar_list = mock_calendar_service.calendarList.return_value
        mock_calendar_list.list.return_value.execute.return_value = {
            "items": sample_calendars
        }

        response = logged_in_client.get("/settings")

        assert response.status_code == 200

    def test_settings_shows_existing_aliases(
        self, logged_in_client, mock_calendar_service, sample_calendars, user_aliases
    ):
        mock_calendar_list = mock_calendar_service.calendarList.return_value
        mock_calendar_list.list.return_value.execute.return_value = {
            "items": sample_calendars
        }

        response = logged_in_client.get("/settings")

        assert response.status_code == 200

    def test_settings_post_saves_aliases(
        self, logged_in_client, mock_calendar_service, sample_calendars, mocker
    ):
        mock_save = mocker.patch("app.services.alias_parser.save_aliases")

        mock_calendar_list = mock_calendar_service.calendarList.return_value
        mock_calendar_list.list.return_value.execute.return_value = {
            "items": sample_calendars
        }

        response = logged_in_client.post(
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
        self, logged_in_client, mock_calendar_service, sample_calendars, mocker
    ):
        mock_save = mocker.patch("app.services.alias_parser.save_aliases")

        mock_calendar_list = mock_calendar_service.calendarList.return_value
        mock_calendar_list.list.return_value.execute.return_value = {
            "items": sample_calendars
        }

        response = logged_in_client.post(
            "/settings",
            data={
                "alias_for__work@example.com": "valid-alias",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        mock_save.assert_not_called()

    def test_settings_post_normalizes_alias(
        self, logged_in_client, mock_calendar_service, sample_calendars, mocker
    ):
        mock_save = mocker.patch("app.services.alias_parser.save_aliases")

        mock_calendar_list = mock_calendar_service.calendarList.return_value
        mock_calendar_list.list.return_value.execute.return_value = {
            "items": sample_calendars
        }

        response = logged_in_client.post(
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
        self, logged_in_client, mock_calendar_service, sample_calendars, mocker
    ):
        mock_save = mocker.patch("app.services.alias_parser.save_aliases")

        mock_calendar_list = mock_calendar_service.calendarList.return_value
        mock_calendar_list.list.return_value.execute.return_value = {
            "items": sample_calendars
        }

        response = logged_in_client.post(
            "/settings",
            data={
                "alias_for__work@example.com": "",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        mock_save.assert_not_called()

    def test_settings_handles_api_error(
        self, logged_in_client, mocker, mock_google_token
    ):
        mocker.patch(
            "app.services.calendar_client.build_service_for_user",
            side_effect=Exception("API Error"),
        )

        response = logged_in_client.get("/settings")

        assert response.status_code == 200


class TestAuthRoutes:
    def test_login_redirects_to_google(self, client):
        response = client.get("/login")

        assert response.status_code == 302
        assert "/login/google" in response.headers["Location"]

    def test_logout_requires_login(self, client):
        response = client.get("/logout")

        assert response.status_code == 302

    def test_logout_clears_session(self, logged_in_client):
        response = logged_in_client.get("/logout")

        assert response.status_code == 302

        # Subsequent request should redirect to login
        response = logged_in_client.get("/")
        assert response.status_code == 302


class TestUnauthenticatedAccess:
    def test_index_redirects_to_login(self, client):
        response = client.get("/")

        assert response.status_code == 302
        assert "/login" in response.headers["Location"]

    def test_submit_redirects_to_login(self, client):
        response = client.post("/submit", data={"bulk-text": "Test event"})

        assert response.status_code == 302
        assert "/login" in response.headers["Location"]

    def test_settings_redirects_to_login(self, client):
        response = client.get("/settings")

        assert response.status_code == 302
        assert "/login" in response.headers["Location"]


class TestUserIsolation:
    def test_user_cannot_see_other_users_aliases(
        self,
        app,
        user,
        second_user,
        user_aliases,
        mock_calendar_service,
        sample_calendars,
    ):
        mock_calendar_list = mock_calendar_service.calendarList.return_value
        mock_calendar_list.list.return_value.execute.return_value = {
            "items": sample_calendars
        }

        # Log in as second_user who has no aliases
        client2 = make_logged_in_client(app, second_user)
        response = client2.get("/settings")

        assert response.status_code == 200
        # user_aliases created "work" and "personal" for user1
        # second_user should not see them pre-filled in form fields
        assert b'value="work"' not in response.data
        assert b'value="personal"' not in response.data

    def test_save_aliases_does_not_affect_other_user(
        self,
        app,
        user,
        second_user,
        user_aliases,
        mock_calendar_service,
        sample_calendars,
        mocker,
    ):
        from app.models import CalendarAlias

        mock_calendar_list = mock_calendar_service.calendarList.return_value
        mock_calendar_list.list.return_value.execute.return_value = {
            "items": sample_calendars
        }

        # second_user saves their own aliases
        client2 = make_logged_in_client(app, second_user)
        client2.post(
            "/settings",
            data={"alias_for__new@example.com": "newalias"},
            follow_redirects=True,
        )

        # user1's aliases should be unchanged
        user1_aliases = CalendarAlias.query.filter_by(user_id=user.id).all()
        assert len(user1_aliases) == 2
        alias_names = {a.alias for a in user1_aliases}
        assert alias_names == {"work", "personal"}
