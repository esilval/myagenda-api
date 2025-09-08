from __future__ import annotations

from flask import Blueprint, request, jsonify

from src.database import get_db
from src.dto.user_dto import UserReadDTO
from src.services.auth_service import AuthService


bp = Blueprint("auth", __name__)


@bp.post("/login")
def login():
    body = request.get_json(force=True) or {}
    identifier = body.get("identifier") or body.get("email") or body.get("nickname")
    password = body.get("password")
    if not identifier or not password:
        return jsonify({"error": "MISSING_CREDENTIALS"}), 400
    db = next(get_db())
    try:
        token = AuthService(db).login(identifier, password)
        return jsonify({"access_token": token, "token_type": "bearer", "expires_in": 1800}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    finally:
        db.close()


@bp.get("/auth")
def auth():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return jsonify({"error": "MISSING_TOKEN"}), 401
    token = auth_header.split(" ", 1)[1]
    db = next(get_db())
    try:
        user = AuthService(db).authenticate(token)
        dto = UserReadDTO(
            id=user.id,
            name=user.name,
            email=user.email,
            nickname=user.nickname,
            company=user.company,
            status=user.status.value,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
        return jsonify(dto.model_dump()), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    finally:
        db.close()


