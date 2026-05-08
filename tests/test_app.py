import copy

from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

INITIAL_ACTIVITIES = {
    name: {
        "description": data["description"],
        "schedule": data["schedule"],
        "max_participants": data["max_participants"],
        "participants": list(data["participants"]),
    }
    for name, data in activities.items()
}


def reset_app_state():
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))


def test_get_activities():
    reset_app_state()

    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_for_activity_success():
    reset_app_state()

    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "test.student@mergington.edu"},
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Signed up test.student@mergington.edu for Chess Club"}
    assert "test.student@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_for_activity_duplicate():
    reset_app_state()

    existing_email = activities["Chess Club"]["participants"][0]
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": existing_email},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant_success():
    reset_app_state()

    email = activities["Programming Class"]["participants"][0]
    response = client.delete(
        "/activities/Programming Class/participants",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from Programming Class"}
    assert email not in activities["Programming Class"]["participants"]


def test_remove_participant_not_found():
    reset_app_state()

    response = client.delete(
        "/activities/Programming Class/participants",
        params={"email": "missing@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
