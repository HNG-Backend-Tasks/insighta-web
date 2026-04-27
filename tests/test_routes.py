import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
from .conftest import MOCK_PROFILES_RESPONSE, MOCK_USER

client = TestClient(app, follow_redirects=False)

def test_unauthenticated_dashboard_redirects_to_login():
    response = client.get("/dashboard")
    assert response.status_code in (302, 307)
    assert "/login" in response.headers["location"]

def test_login_page_renders():
    response = client.get("/login")
    assert response.status_code == 200
    assert "GitHub" in response.text

def test_dashboard_renders(mock_context):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.side_effect = [
        {"total": 100},  # total profiles call
        {"total": 60},   # male call
        {"total": 40},   # female call
    ]
    mock_context.get.return_value = mock_response

    response = client.get("/dashboard", cookies={"access_token": "fake_token"})
    assert response.status_code == 200
    assert "Dashboard" in response.text

def test_profiles_list_renders(mock_context):
    response = client.get("/profiles", cookies={"access_token": "fake_token"})
    assert response.status_code == 200
    assert "Kwame" in response.text

def test_profile_detail_renders(mock_context):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": MOCK_PROFILES_RESPONSE["data"][0]}
    mock_context.get.return_value = mock_response

    response = client.get("/profiles/abc-123", cookies={"access_token": "fake_token"})
    assert response.status_code == 200
    assert "Kwame" in response.text

def test_search_page_renders(mock_context):
    response = client.get("/search?q=males+from+nigeria", cookies={"access_token": "fake_token"})
    assert response.status_code == 200
    assert "Kwame" in response.text

def test_account_page_renders(mock_context):
    response = client.get("/account", cookies={"access_token": "fake_token"})
    assert response.status_code == 200
    assert "danielpopoola" in response.text

def test_analyst_cannot_see_delete_button(mock_context):
    from app.dependencies import get_portal_context
    from app.main import app

    analyst_user = {**MOCK_USER, "role": "analyst"}
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": MOCK_PROFILES_RESPONSE["data"][0]}
    mock_context.get.return_value = mock_response

    # override with analyst user
    app.dependency_overrides[get_portal_context] = lambda: {
        "client": mock_context,
        "user": analyst_user,
    }

    response = client.get("/profiles/abc-123", cookies={"access_token": "fake_token"})

    # restore admin override
    app.dependency_overrides[get_portal_context] = lambda: {
        "client": mock_context,
        "user": MOCK_USER,
    }

    assert response.status_code == 200
    assert "Delete Profile" not in response.text