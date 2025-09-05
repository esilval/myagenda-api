from __future__ import annotations

from functools import wraps
from flask import request, jsonify, g

from src.database import SessionLocal
from src.services.auth_service import AuthService


def require_auth(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "MISSING_TOKEN"}), 401
        token = auth_header.split(" ", 1)[1]
        db = SessionLocal()
        try:
            user = AuthService(db).authenticate(token)
            g.current_user = user
            return fn(*args, **kwargs)
        except Exception:
            return jsonify({"error": "INVALID_TOKEN"}), 401
        finally:
            db.close()

    return wrapper


