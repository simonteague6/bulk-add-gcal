import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def app():
    from app import create_app

    test_app = create_app()
    test_app.config["TESTING"] = True
    test_app.config["SECRET_KEY"] = "test-secret-key"
    yield test_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def mock_aliases_file(tmp_path, monkeypatch):
    aliases_data = {"work": "work@example.com", "personal": "personal@example.com"}
    aliases_file = tmp_path / "calendar_aliases.json"
    import json

    aliases_file.write_text(json.dumps(aliases_data))
    monkeypatch.setattr(
        "app.services.alias_parser.load_aliases",
        lambda path=None: aliases_data,
    )
    yield aliases_data


@pytest.fixture
def mock_credentials(mocker):
    mock_creds = mocker.MagicMock()
    mock_creds.valid = True
    mock_creds.expired = False
    mocker.patch(
        "app.services.calendar_client.load_credentials", return_value=mock_creds
    )
    return mock_creds


@pytest.fixture
def mock_calendar_service(mocker, mock_credentials):
    mock_service = mocker.MagicMock()
    mocker.patch(
        "app.services.calendar_client.build_service", return_value=mock_service
    )
    return mock_service


@pytest.fixture
def sample_calendars():
    return [
        {
            "id": "primary@example.com",
            "summary": "Primary Calendar",
            "accessRole": "owner",
            "primary": True,
        },
        {
            "id": "work@example.com",
            "summary": "Work Calendar",
            "accessRole": "writer",
        },
        {
            "id": "readonly@example.com",
            "summary": "Read Only Calendar",
            "accessRole": "reader",
        },
    ]
