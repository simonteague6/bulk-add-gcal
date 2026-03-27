import pytest


def make_logged_in_client(app, user):
    """Create a test client logged in as the given user."""
    client = app.test_client()
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user.id)
    return client


@pytest.fixture
def app():
    from app import create_app

    test_app = create_app(
        test_config={
            "TESTING": True,
            "SECRET_KEY": "test-secret-key",
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        }
    )
    with test_app.app_context():
        from app.models import db

        db.create_all()
        yield test_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def user(app):
    from app.models import db, User

    u = User(id=1, email="test@example.com", name="Test User")
    db.session.add(u)
    db.session.commit()
    return u


@pytest.fixture
def second_user(app):
    from app.models import db, User

    u = User(id=2, email="other@example.com", name="Other User")
    db.session.add(u)
    db.session.commit()
    return u


@pytest.fixture
def logged_in_client(app, user):
    return make_logged_in_client(app, user)


@pytest.fixture
def mock_google_token(mocker):
    token = {
        "access_token": "fake-access-token",
        "refresh_token": "fake-refresh-token",
        "token_type": "Bearer",
        "expires_in": 3600,
    }
    mock_google = mocker.MagicMock()
    mock_google.token = token
    mocker.patch("app.events.routes.google", mock_google)
    mocker.patch("app.settings.routes.google", mock_google)
    return token


@pytest.fixture
def mock_calendar_service(mocker, mock_google_token):
    mock_service = mocker.MagicMock()
    mocker.patch(
        "app.services.calendar_client.build_service_for_user",
        return_value=mock_service,
    )
    return mock_service


@pytest.fixture
def user_aliases(app, user):
    from app.models import db, CalendarAlias

    aliases = [
        CalendarAlias(user_id=user.id, alias="work", calendar_id="work@example.com"),
        CalendarAlias(
            user_id=user.id, alias="personal", calendar_id="personal@example.com"
        ),
    ]
    db.session.add_all(aliases)
    db.session.commit()
    return {"work": "work@example.com", "personal": "personal@example.com"}


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
