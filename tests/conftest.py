from unittest.mock import patch, MagicMock
import pytest

MOCK_USER = {
    "id": "abc-123",
    "username": "danielpopoola",
    "email": "daniel@example.com",
    "role": "admin",
    "avatar_url": "https://github.com/avatar.png",
    "created_at": "2026-01-01T00:00:00",
}

MOCK_PROFILES_RESPONSE = {
    "status": "success",
    "page": 1,
    "limit": 10,
    "total": 2,
    "total_pages": 1,
    "links": {"self": "/api/profiles?page=1&limit=10", "next": None, "prev": None},
    "data": [
        {
            "id": "abc-123",
            "name": "Kwame",
            "gender": "male",
            "gender_probability": 0.95,
            "age": 25,
            "age_group": "adult",
            "country_id": "NG",
            "country_name": "Nigeria",
            "country_probability": 0.85,
            "created_at": "2026-01-01"
        },
    ]
}

@pytest.fixture
def mock_context():
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = MOCK_PROFILES_RESPONSE
    mock_client.get.return_value = mock_response

    context = {"client": mock_client, "user": MOCK_USER}

    from app.dependencies import get_portal_context
    from app.main import app

    app.dependency_overrides[get_portal_context] = lambda: context
    yield mock_client
    app.dependency_overrides.clear()