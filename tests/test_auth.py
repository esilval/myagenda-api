from src.app import app
from src.database import SessionLocal
from src.models.user import User


def _login(identifier: str, password: str) -> str:
    client = app.test_client()
    r = client.post("/login", json={"identifier": identifier, "password": password})
    assert r.status_code == 200, r.get_json()
    return r.get_json()["access_token"]


def _create_user(email: str, nickname: str | None, password: str = "secretpass") -> str:
    client = app.test_client()
    res = client.post(
        "/users",
        json={"name": "Auth U", "email": email, "nickname": nickname, "password": password},
    )
    assert res.status_code == 201, res.get_json()
    return res.get_json()["id"]


def test_login_with_email_and_auth():
    client = app.test_client()
    email = f"auth_{id(object())}@example.com"
    user_id = _create_user(email, f"authnick_{id(object())}")

    # login with email
    r = client.post("/login", json={"identifier": email, "password": "secretpass"})
    assert r.status_code == 200, r.get_json()
    token = r.get_json()["access_token"]

    # auth
    r2 = client.get("/auth", headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 200
    data = r2.get_json()
    assert data["email"] == email
    assert "password" not in data


def test_login_with_nickname_and_inactive_user_denied():
    client = app.test_client()
    email = f"auth2_{id(object())}@example.com"
    nick = f"nick_{id(object())}"
    user_id = _create_user(email, nick, password="pass123456")

    # deactivate user
    token = _login(email, "pass123456")
    r0 = client.post(f"/users/{user_id}/deactivate", headers={"Authorization": f"Bearer {token}"})
    assert r0.status_code == 200

    # login with nickname should fail
    r = client.post("/login", json={"identifier": nick, "password": "pass123456"})
    assert r.status_code == 401
    assert r.get_json()["error"] == "INVALID_CREDENTIALS"


