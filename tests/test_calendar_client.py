import pytest

from app.services import calendar_client


class TestLoadCredentials:
    def test_load_credentials_from_existing_token(self, mocker, tmp_path):
        mock_creds = mocker.MagicMock()
        mock_creds.valid = True
        mock_creds.expired = False

        mocker.patch("os.path.exists", return_value=True)
        mocker.patch(
            "app.services.calendar_client.Credentials.from_authorized_user_file",
            return_value=mock_creds,
        )

        result = calendar_client.load_credentials()

        assert result == mock_creds

    def test_load_credentials_refreshes_expired(self, mocker, tmp_path):
        mock_creds = mocker.MagicMock()
        mock_creds.valid = False
        mock_creds.expired = True
        mock_creds.refresh_token = "refresh_token"
        mock_creds.to_json.return_value = '{"token": "refreshed"}'

        mocker.patch("os.path.exists", return_value=True)
        mocker.patch(
            "app.services.calendar_client.Credentials.from_authorized_user_file",
            return_value=mock_creds,
        )
        mocker.patch("builtins.open", mocker.mock_open())

        result = calendar_client.load_credentials()

        mock_creds.refresh.assert_called_once()
        assert result == mock_creds

    def test_load_credentials_no_token_starts_flow(self, mocker, tmp_path):
        mock_creds = mocker.MagicMock()
        mock_creds.valid = True
        mock_creds.to_json.return_value = '{"token": "test"}'

        mock_flow = mocker.MagicMock()
        mock_flow.run_local_server.return_value = mock_creds

        mocker.patch("os.path.exists", return_value=False)
        mocker.patch(
            "app.services.calendar_client.InstalledAppFlow.from_client_secrets_file",
            return_value=mock_flow,
        )
        mock_open = mocker.patch("builtins.open", mocker.mock_open())

        result = calendar_client.load_credentials()

        mock_flow.run_local_server.assert_called_once()
        assert result == mock_creds


class TestBuildService:
    def test_build_service_returns_service(self, mocker):
        mock_creds = mocker.MagicMock()
        mock_service = mocker.MagicMock()

        mocker.patch(
            "app.services.calendar_client.load_credentials", return_value=mock_creds
        )
        mocker.patch("app.services.calendar_client.build", return_value=mock_service)

        result = calendar_client.build_service()

        assert result == mock_service


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
