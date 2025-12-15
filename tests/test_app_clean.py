from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_root_redirect():
    resp = client.get("/", follow_redirects=False)
    assert resp.status_code in (301, 302, 307, 308)
    assert resp.headers.get("location") == "/static/index.html"


def test_get_activities_contains_known_activity():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_success_and_duplicate():
    activity = "Gym Class"
    email = "test_student@example.com"

    resp = client.get("/activities")
    activities = resp.json()
    participants = activities.get(activity, {}).get("participants", [])
    # Ensure test idempotency: remove if already present
    if email in participants:
        participants.remove(email)

    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200

    resp = client.get("/activities")
    activities = resp.json()
    assert email in activities.get(activity, {}).get("participants", [])

    # Duplicate
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 400
