from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_root_redirect():
    # Use TestClient parameter name used by starlette/fastapi
    resp = client.get("/", follow_redirects=False)
    assert resp.status_code in (301, 302, 307, 308)
    assert resp.headers.get("location") == "/static/index.html"


def test_get_activities_contains_known_activity():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # known activity from the in-memory DB
    assert "Chess Club" in data


def test_signup_success_and_duplicate():
    activity = "Gym Class"
    email = "test_student@example.com"

    # ensure the email is not already present
    resp = client.get("/activities")
    assert resp.status_code == 200
    activities = resp.json()
    participants = activities.get(activity, {}).get("participants", [])
    if email in participants:
        # remove if present to keep test idempotent
        participants.remove(email)

    # Signup (email is expected as query parameter for this app signature)
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200
    assert email in resp.json().get("message", "")

    # Confirm participant was added in the in-memory store
    resp = client.get("/activities")
    assert resp.status_code == 200
    activities = resp.json()
    assert email in activities.get(activity, {}).get("participants", [])

    # Attempt duplicate signup -> should return 400
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 400
