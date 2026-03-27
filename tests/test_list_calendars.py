from app.services.list_calendars import list_calendars


class TestListCalendars:
    def test_list_calendars_single_page(self, mocker):
        mock_service = mocker.MagicMock()
        mock_calendar_list = mocker.MagicMock()
        mock_service.calendarList.return_value = mock_calendar_list

        mock_response = {
            "items": [
                {"id": "cal1@example.com", "summary": "Calendar 1"},
                {"id": "cal2@example.com", "summary": "Calendar 2"},
            ]
        }
        mock_calendar_list.list.return_value.execute.return_value = mock_response

        result = list_calendars(mock_service)

        assert len(result) == 2
        assert result[0]["id"] == "cal1@example.com"
        assert result[1]["id"] == "cal2@example.com"

    def test_list_calendars_multiple_pages(self, mocker):
        mock_service = mocker.MagicMock()
        mock_calendar_list = mocker.MagicMock()
        mock_service.calendarList.return_value = mock_calendar_list

        mock_calendar_list.list.side_effect = [
            mocker.MagicMock(
                execute=mocker.MagicMock(
                    return_value={
                        "items": [{"id": "cal1@example.com", "summary": "Calendar 1"}],
                        "nextPageToken": "token123",
                    }
                )
            ),
            mocker.MagicMock(
                execute=mocker.MagicMock(
                    return_value={
                        "items": [{"id": "cal2@example.com", "summary": "Calendar 2"}],
                    }
                )
            ),
        ]

        result = list_calendars(mock_service)

        assert len(result) == 2
        assert result[0]["id"] == "cal1@example.com"
        assert result[1]["id"] == "cal2@example.com"

    def test_list_calendars_empty(self, mocker):
        mock_service = mocker.MagicMock()
        mock_calendar_list = mocker.MagicMock()
        mock_service.calendarList.return_value = mock_calendar_list

        mock_calendar_list.list.return_value.execute.return_value = {"items": []}

        result = list_calendars(mock_service)

        assert result == []

    def test_list_calendars_no_items_key(self, mocker):
        mock_service = mocker.MagicMock()
        mock_calendar_list = mocker.MagicMock()
        mock_service.calendarList.return_value = mock_calendar_list

        mock_calendar_list.list.return_value.execute.return_value = {}

        result = list_calendars(mock_service)

        assert result == []
