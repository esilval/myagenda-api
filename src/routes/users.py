from __future__ import annotations

from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from src.database import get_db
from src.dto.user_dto import UserCreateDTO, UserUpdateDTO
from src.services.user_service import UserService
from src.utils.auth import require_auth


bp = Blueprint("users", __name__, url_prefix="/users")


@bp.post("")
def create_user():
    try:
        dto = UserCreateDTO(**request.get_json(force=True))
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400
    db = next(get_db())
    try:
        service = UserService(db)
        user = service.create_user(dto)
        return jsonify(user.model_dump()), 201
    except ValueError as e:
        code = 409 if str(e) in {"EMAIL_TAKEN", "NICKNAME_TAKEN"} else 400
        return jsonify({"error": str(e)}), code


@bp.patch("/<user_id>")
@require_auth
def update_user(user_id: str):
    try:
        dto = UserUpdateDTO(**request.get_json(force=True))
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400
    db = next(get_db())
    try:
        service = UserService(db)
        user = service.update_user(user_id, dto)
        return jsonify(user.model_dump()), 200
    except ValueError as e:
        msg = str(e)
        if msg == "User not found":
            return jsonify({"error": msg}), 404
        if msg == "NICKNAME_TAKEN":
            return jsonify({"error": msg}), 409
        return jsonify({"error": msg}), 400


@bp.post("/<user_id>/activate")
@require_auth
def activate_user(user_id: str):
    db = next(get_db())
    try:
        service = UserService(db)
        user = service.set_active(user_id, True)
        return jsonify(user.model_dump()), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404


@bp.post("/<user_id>/deactivate")
@require_auth
def deactivate_user(user_id: str):
    db = next(get_db())
    try:
        service = UserService(db)
        user = service.set_active(user_id, False)
        return jsonify(user.model_dump()), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404


