import uuid

from src.app import app
def _login(email_or_nick: str, password: str) -> str:
    client = app.test_client()
    r = client.post("/login", json={"identifier": email_or_nick, "password": password})
    assert r.status_code == 200, r.get_json()
    return r.get_json()["access_token"]


_WEIGHTS = [3, 7, 13, 17, 19, 23, 29, 37, 41]


def build_valid_nit(base: str) -> str:
    total = 0
    for i, ch in enumerate(reversed(base)):
        total += int(ch) * _WEIGHTS[i]
    remainder = total % 11
    dv = remainder if remainder in (0, 1) else 11 - remainder
    return f"{base}-{dv}"


def test_create_update_list_delete_client():
    client = app.test_client()

    # create company first with valid NIT
    base = ''.join(str(int(x, 16) % 10) for x in uuid.uuid4().hex[:9])
    comp_nit = build_valid_nit(base)
    # crear usuario y token para auth
    uemail = f"u{uuid.uuid4().hex[:8]}@example.com"
    ures = client.post("/users", json={"name": "Ops", "email": uemail, "password": "pass123456"})
    assert ures.status_code == 201
    token = _login(uemail, "pass123456")

    rcomp = client.post(
        "/companies",
        json={"nit": comp_nit, "business_name": f"Comp-{uuid.uuid4().hex[:6]}"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert rcomp.status_code == 201
    company_id = rcomp.get_json()["id"]

    email = f"client_{uuid.uuid4().hex[:8]}@example.com"
    phone = f"+57-3{uuid.uuid4().hex[:10]}"
    r1 = client.post(
        "/clients",
        json={
            "company_id": company_id,
            "email": email,
            "phone": phone,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r1.status_code == 201, r1.get_json()
    cid = r1.get_json()["id"]

    # try duplicate email
    rdup = client.post(
        "/clients",
        json={
            "company_id": company_id,
            "email": email,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert rdup.status_code == 409

    # update
    r2 = client.put(
        f"/clients/{cid}",
        json={
            "company_id": company_id,
            "email": email,
            "phone": phone,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r2.status_code == 200
    assert r2.get_json()["company_id"] == company_id

    # list paginated
    r3 = client.get("/clients?page=1&size=10&q=client_", headers={"Authorization": f"Bearer {token}"})
    assert r3.status_code == 200
    data = r3.get_json()
    assert data["total"] >= 1
    assert any(item["id"] == cid for item in data["items"])

    # deactivate
    r4 = client.post(f"/clients/{cid}/deactivate", headers={"Authorization": f"Bearer {token}"})
    assert r4.status_code == 200
    assert r4.get_json()["status"] == "INACTIVE"

    # delete
    r5 = client.delete(f"/clients/{cid}", headers={"Authorization": f"Bearer {token}"})
    assert r5.status_code == 204


