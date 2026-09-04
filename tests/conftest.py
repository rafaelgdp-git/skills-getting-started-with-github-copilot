import pytest

from src import app as app_module


@pytest.fixture(autouse=True)
def isolated_application_state(tmp_path, monkeypatch):
    activities = {
        "Chess Club": {
            "description": "Learn strategies",
            "schedule": "Fridays",
            "max_participants": 2,
            "participants": ["existing@example.com"],
        },
        "Club & Art": {
            "description": "Explore art",
            "schedule": "Wednesdays",
            "max_participants": 2,
            "participants": [],
        },
    }
    activities_file = tmp_path / "activities.json"

    monkeypatch.setattr(app_module, "activities", activities)
    monkeypatch.setattr(app_module, "activities_file", activities_file)

    yield