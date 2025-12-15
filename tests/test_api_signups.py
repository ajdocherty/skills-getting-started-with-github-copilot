from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_api_get_activities_and_signups():
    resp = client.get("/api/activities")
    assert resp.status_code == 200
    acts = resp.json()
    assert isinstance(acts, list)
    assert any(a["name"] == "Chess Club" for a in acts)

    resp2 = client.get("/api/signups")
    assert resp2.status_code == 200
    signups = resp2.json()
    assert isinstance(signups, list)


def test_api_post_and_delete_signup():
    activity = "Gym Class"
    email = "delete_me@example.com"

    # ensure clean state
    resp = client.get("/api/signups")
    signups = resp.json()
    for s in list(signups):
        if s.get("email") == email and s.get("activityId") == activity:
            # remove if present
            client.request("DELETE", "/api/signups", json={"email": email, "activityId": activity})

    # add signup
    resp = client.post("/api/signups", json={"email": email, "activityId": activity})
    assert resp.status_code == 200
    assert "Signed up" in resp.json().get("message", "")

    # confirm exists
    resp = client.get("/api/signups")
    assert any(s["email"] == email and s["activityId"] == activity for s in resp.json())

    # delete signup
    resp = client.request("DELETE", "/api/signups", json={"email": email, "activityId": activity})
    assert resp.status_code == 200
    assert "Removed" in resp.json().get("message", "")

    # confirm removed
    resp = client.get("/api/signups")
    assert not any(s["email"] == email and s["activityId"] == activity for s in resp.json())
