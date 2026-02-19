from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def auth_headers():
    r = client.post(
        "/api/v1/auth/login", json={"username": "admin", "password": "Admin@123"}
    )
    assert r.status_code == 200
    token = r.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_auth_login_refresh_logout():
    login = client.post(
        "/api/v1/auth/login", json={"username": "admin", "password": "Admin@123"}
    )
    assert login.status_code == 200
    assert login.json()["ok"] is True
    refresh = login.json()["data"]["refresh_token"]

    rr = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh})
    assert rr.status_code == 200
    access = rr.json()["data"]["access_token"]

    out = client.post(
        "/api/v1/auth/logout", headers={"Authorization": f"Bearer {access}"}
    )
    assert out.status_code == 200


def test_incidents_crud_and_actions():
    headers = auth_headers()
    payload = {
        "title": "Slip incident",
        "description": "wet floor",
        "site": "Plant-1",
        "department": "Ops",
        "severity": 4,
        "likelihood": 3,
        "status": "open",
    }
    r = client.post("/api/v1/incidents", json=payload, headers=headers)
    assert r.status_code == 200
    incident_id = r.json()["data"]["id"]
    assert r.json()["data"]["risk_score"] == 12

    g = client.get(f"/api/v1/incidents/{incident_id}")
    assert g.status_code == 200

    payload["likelihood"] = 5
    u = client.patch(f"/api/v1/incidents/{incident_id}", json=payload, headers=headers)
    assert u.status_code == 200
    assert u.json()["data"]["risk_score"] == 20

    act = client.post(
        f"/api/v1/incidents/{incident_id}/actions",
        json={"action_text": "fix floor", "owner": "hse", "due_date": "2030-01-01"},
    )
    assert act.status_code == 200


def test_dashboard_overview_non_zero_seeded():
    o = client.get("/api/v1/dashboard/overview")
    assert o.status_code == 200
    data = o.json()["data"]
    assert "connected_status" in data
    assert data["counters"]["cameras_total"] >= 1
    assert isinstance(data["last_incidents"], list)


def test_cameras_and_vision_events():
    c = client.get("/api/v1/cameras")
    assert c.status_code == 200
    assert isinstance(c.json()["data"], list)

    ve = client.get("/api/v1/vision/events")
    assert ve.status_code == 200
    assert isinstance(ve.json()["data"], list)


def test_rules_engine_trigger():
    run = client.post("/api/v1/rules/run")
    assert run.status_code == 200
    events = client.get("/api/v1/rules/events")
    assert events.status_code == 200
    assert isinstance(events.json()["data"], list)
