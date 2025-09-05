import uuid

from src.app import app
from src.database import SessionLocal
from src.models.user import User
from src.utils.security import verify_password


def _unique_email() -> str:
    return f"user_{uuid.uuid4().hex[:12]}@example.com"

def _unique_nick() -> str:
    return f"nick_{uuid.uuid4().hex[:8]}"


def _login(email_or_nick: str, password: str) -> str:
    client = app.test_client()
    r = client.post("/login", json={"identifier": email_or_nick, "password": password})
    assert r.status_code == 200, r.get_json()
    return r.get_json()["access_token"]


def test_create_user_should_hash_and_hide_password():
    client = app.test_client()
    email = _unique_email()

    res = client.post(
        "/users",
        json={
            "name": "Alice",
            "email": email,
            "password": "mysecretpass",
        },
    )
    assert res.status_code == 201, res.get_json()
    data = res.get_json()
    assert "password" not in data
    assert data["email"] == email
    assert data["status"] == "ACTIVE"

    # Verify password is hashed in DB
    db = SessionLocal()
    try:
        user = db.get(User, data["id"])  # type: ignore[index]
        assert user is not None
        assert user.password != "mysecretpass"
        assert verify_password("mysecretpass", user.password)
    finally:
        db.close()


def test_update_user_changes_password_and_nickname():
    client = app.test_client()
    email = _unique_email()

    # create first
    res = client.post(
        "/users",
        json={
            "name": "Bob",
            "email": email,
            "password": "initialpass",
        },
    )
    assert res.status_code == 201
    user_id = res.get_json()["id"]

    # update password and nickname
    new_nick = _unique_nick()
    token = _login(email, "initialpass")
    res2 = client.patch(
        f"/users/{user_id}",
        json={
            "password": "newsecurepass",
            "nickname": new_nick,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res2.status_code == 200, res2.get_json()
    data2 = res2.get_json()
    assert data2["nickname"] == new_nick
    assert "password" not in data2

    # DB verify
    db = SessionLocal()
    try:
        user = db.get(User, user_id)
        assert user is not None
        assert verify_password("newsecurepass", user.password)
    finally:
        db.close()


def test_activate_deactivate_user():
    client = app.test_client()
    email = _unique_email()
    res = client.post(
        "/users",
        json={
            "name": "Carol",
            "email": email,
            "password": "carolpass",
        },
    )
    assert res.status_code == 201
    user_id = res.get_json()["id"]

    # deactivate
    token = _login(email, "carolpass")
    r1 = client.post(f"/users/{user_id}/deactivate", headers={"Authorization": f"Bearer {token}"})
    assert r1.status_code == 200
    assert r1.get_json()["status"] == "INACTIVE"

    # activate (necesita token válido; tras desactivar, el login por email sigue permitiendo obtener token
    # del mismo usuario que acabamos de desactivar, pero el servicio AuthService impide usarlo si usuario INACTIVE.
    # Para el test, creamos un segundo usuario operador que activa al primero.)
    op_email = _unique_email()
    r_op = client.post(
        "/users",
        json={"name": "Operator", "email": op_email, "password": "opsecret"},
    )
    assert r_op.status_code == 201
    op_token = _login(op_email, "opsecret")
    r2 = client.post(f"/users/{user_id}/activate", headers={"Authorization": f"Bearer {op_token}"})
    assert r2.status_code == 200
    assert r2.get_json()["status"] == "ACTIVE"


def test_duplicate_email_and_nickname_conflicts():
    client = app.test_client()
    email = _unique_email()

    # create baseline user
    base_nick = _unique_nick()
    r1 = client.post(
        "/users",
        json={"name": "U1", "email": email, "password": "pass123456", "nickname": base_nick},
    )
    assert r1.status_code == 201
    uid = r1.get_json()["id"]

    # duplicate email
    r2 = client.post(
        "/users",
        json={"name": "U2", "email": email, "password": "pass123456"},
    )
    assert r2.status_code == 409
    assert r2.get_json()["error"] == "EMAIL_TAKEN"

    # duplicate nickname on another user
    r3 = client.post(
        "/users",
        json={"name": "U3", "email": _unique_email(), "password": "pass123456", "nickname": base_nick},
    )
    assert r3.status_code == 409
    assert r3.get_json()["error"] == "NICKNAME_TAKEN"

    # trying to update another user to same nickname
    r4 = client.post(
        "/users",
        json={"name": "U4", "email": _unique_email(), "password": "pass123456", "nickname": _unique_nick()},
    )
    assert r4.status_code == 201
    uid2 = r4.get_json()["id"]

    token2 = _login(r4.get_json()["email"], "pass123456")
    r5 = client.patch(f"/users/{uid2}", json={"nickname": base_nick}, headers={"Authorization": f"Bearer {token2}"})
    assert r5.status_code == 409
    assert r5.get_json()["error"] == "NICKNAME_TAKEN"


