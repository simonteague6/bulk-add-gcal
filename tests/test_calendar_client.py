import os

from app.services import calendar_client


class TestBuildServiceForUser:
    def test_builds_credentials_from_token(self, mocker):
        mocker.patch.dict(
            os.environ,
            {
                "GOOGLE_CLIENT_ID": "test-client-id",
                "GOOGLE_CLIENT_SECRET": "test-client-secret",
            },
        )
        mock_creds = mocker.MagicMock()
        mocker.patch(
            "app.services.calendar_client.Credentials", return_value=mock_creds
        )
        mock_build = mocker.patch(
            "app.services.calendar_client.build", return_value=mocker.MagicMock()
        )

        token = {
            "access_token": "test-access-token",
            "refresh_token": "test-refresh-token",
            "token_type": "Bearer",
            "expires_in": 3600,
        }

        result = calendar_client.build_service_for_user(token)

        mock_build.assert_called_once_with("calendar", "v3", credentials=mock_creds)
        assert result == mock_build.return_value

    def test_passes_refresh_token(self, mocker):
        mocker.patch.dict(
            os.environ,
            {
                "GOOGLE_CLIENT_ID": "test-client-id",
                "GOOGLE_CLIENT_SECRET": "test-client-secret",
            },
        )
        mock_creds_cls = mocker.patch("app.services.calendar_client.Credentials")
        mocker.patch("app.services.calendar_client.build")

        token = {
            "access_token": "test-access-token",
            "refresh_token": "my-refresh-token",
        }

        calendar_client.build_service_for_user(token)

        call_kwargs = mock_creds_cls.call_args[1]
        assert call_kwargs["token"] == "test-access-token"
        assert call_kwargs["refresh_token"] == "my-refresh-token"


class TestCreateEventQuickAdd:
    def test_create_event_quick_add_success(self, mocker):
        mock_service = mocker.MagicMock()
        mock_events = mocker.MagicMock()
        mock_execute = mocker.MagicMock(
            return_value={"id": "event123", "summary": "Test Event"}
        )

        mock_service.events.return_value = mock_events
        mock_events.quickAdd.return_value.execute = mock_execute

        result = calendar_client.create_event_quick_add(
            mock_service, "calendar@example.com", "Meeting tomorrow at 3pm"
        )

        mock_service.events.assert_called_once()
        mock_events.quickAdd.assert_called_once_with(
            calendarId="calendar@example.com", text="Meeting tomorrow at 3pm"
        )
        assert result == {"id": "event123", "summary": "Test Event"}

    def test_create_event_quick_add_primary_calendar(self, mocker):
        mock_service = mocker.MagicMock()
        mock_events = mocker.MagicMock()
        mock_execute = mocker.MagicMock(return_value={"id": "event456"})

        mock_service.events.return_value = mock_events
        mock_events.quickAdd.return_value.execute = mock_execute

        result = calendar_client.create_event_quick_add(
            mock_service, "primary", "Lunch with team"
        )

        mock_events.quickAdd.assert_called_once_with(
            calendarId="primary", text="Lunch with team"
        )
        assert result == {"id": "event456"}
