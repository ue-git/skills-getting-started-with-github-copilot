import copy
import pytest
from fastapi.testclient import TestClient

from src import app, activities

client = TestClient(app)

# snapshot of original activities so tests can reset state
ORIGINAL_ACTIVITIES = copy.deepcopy(activities)

@pytest.fixture(autouse=True)
def reset_activities():
    # Arrange: restore the shared activities dict before each test
    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))


def test_get_activities_returns_dictionary():
    # Act
    resp = client.get("/activities")
    # Assert
    assert resp.status_code == 200
    assert isinstance(resp.json(), dict)
    assert "Chess Club" in resp.json()


def test_signup_adds_participant_and_returns_message():
    # Arrange
    email = "test@example.com"
    activity = "Chess Club"
    # Act
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert resp.status_code == 200
    data = resp.json()
    assert "Signed up" in data.get("message", "")
    assert email in activities[activity]["participants"]


def test_duplicate_signup_returns_400():
    # Arrange
    activity = "Chess Club"
    email = ORIGINAL_ACTIVITIES[activity]["participants"][0]
    # Act
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert resp.status_code == 400


def test_remove_participant_successfully():
    # Arrange
    activity = "Chess Club"
    email = ORIGINAL_ACTIVITIES[activity]["participants"][0]
    # Act
    resp = client.delete(f"/activities/{activity}/participants?email={email}")
    # Assert
    assert resp.status_code == 200
    assert email not in activities[activity]["participants"]


def test_remove_nonexistent_participant_returns_404():
    # Arrange
    activity = "Chess Club"
    email = "nobody@nowhere.com"
    # Act
    resp = client.delete(f"/activities/{activity}/participants?email={email}")
    # Assert
    assert resp.status_code == 404


def test_operations_on_nonexistent_activity_return_404():
    # Arrange
    email = "foo@bar.com"
    # Act
    signup_resp = client.post(f"/activities/NoSuch/signup?email={email}")
    remove_resp = client.delete(f"/activities/NoSuch/participants?email={email}")
    # Assert
    assert signup_resp.status_code == 404
    assert remove_resp.status_code == 404
