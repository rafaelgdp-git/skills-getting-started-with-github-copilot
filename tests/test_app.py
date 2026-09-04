import json

from fastapi.testclient import TestClient

from src.app import app


client = TestClient(app)


def test_root_redirects_to_static_index():
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_static_index_is_available():
    response = client.get("/static/index.html")

    assert response.status_code == 200
    assert "Mergington High School" in response.text


def test_get_activities_returns_activity_details():
    response = client.get("/activities")

    assert response.status_code == 200
    assert response.json()["Chess Club"] == {
        "description": "Learn strategies",
        "schedule": "Fridays",
        "max_participants": 2,
        "participants": ["existing@example.com"],
    }


def test_signup_adds_participant_and_persists_state():
    response = client.post(
        "/activities/Club%20%26%20Art/signup",
        params={"email": "new@example.com"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Signed up new@example.com for Club & Art"
    }
    assert client.get("/activities").json()["Club & Art"]["participants"] == [
        "new@example.com"
    ]

    from src import app as app_module

    assert json.loads(app_module.activities_file.read_text()) == app_module.activities


def test_signup_rejects_duplicate_participant():
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": "existing@example.com"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_signup_rejects_unknown_activity():
    response = client.post(
        "/activities/Unknown%20Club/signup",
        params={"email": "new@example.com"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant_and_persists_state():
    response = client.delete(
        "/activities/Chess%20Club/signup",
        params={"email": "existing@example.com"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Unregistered existing@example.com from Chess Club"
    }
    assert client.get("/activities").json()["Chess Club"]["participants"] == []

    from src import app as app_module

    assert json.loads(app_module.activities_file.read_text()) == app_module.activities


def test_unregister_rejects_unknown_participant():
    response = client.delete(
        "/activities/Chess%20Club/signup",
        params={"email": "missing@example.com"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_unregister_rejects_unknown_activity():
    response = client.delete(
        "/activities/Unknown%20Club/signup",
        params={"email": "new@example.com"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"