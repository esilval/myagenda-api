from __future__ import annotations

from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from src.database import get_db
from src.dto.company_dto import CompanyCreateDTO
from src.services.company_service import CompanyService
from src.utils.auth import require_auth


bp = Blueprint("companies", __name__, url_prefix="/companies")


@bp.post("")
@require_auth
def create_company():
    try:
        dto = CompanyCreateDTO(**request.get_json(force=True))
    except ValidationError as e:
        return jsonify({"error": [err.get("msg") for err in e.errors()]}), 400
    db = next(get_db())
    try:
        c = CompanyService(db).create(dto)
        return jsonify(c.model_dump()), 201
    except ValueError as e:
        code = 409 if str(e) == "NIT_TAKEN" else 400
        return jsonify({"error": str(e)}), code


@bp.get("")
@require_auth
def list_companies():
    page = int(request.args.get("page", 1))
    size = int(request.args.get("size", 10))
    status = request.args.get("status")
    text = request.args.get("q")
    db = next(get_db())
    total, items = CompanyService(db).list_paginated(page=page, size=size, status=status, text=text)
    return jsonify({"total": total, "items": [i.model_dump() for i in items]}), 200


@bp.get("/<company_id>")
@require_auth
def get_company(company_id: str):
    db = next(get_db())
    try:
        c = CompanyService(db).get(company_id)
        return jsonify(c.model_dump()), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404


@bp.put("/<company_id>")
@require_auth
def update_company(company_id: str):
    try:
        dto = CompanyCreateDTO(**request.get_json(force=True))
    except ValidationError as e:
        return jsonify({"error": [err.get("msg") for err in e.errors()]}), 400
    db = next(get_db())
    try:
        c = CompanyService(db).update(company_id, dto)
        return jsonify(c.model_dump()), 200
    except ValueError as e:
        if str(e) == "NOT_FOUND":
            return jsonify({"error": "NOT_FOUND"}), 404
        if str(e) == "NIT_TAKEN":
            return jsonify({"error": "NIT_TAKEN"}), 409
        return jsonify({"error": str(e)}), 400


@bp.delete("/<company_id>")
@require_auth
def delete_company(company_id: str):
    db = next(get_db())
    try:
        CompanyService(db).delete(company_id)
        return ("", 204)
    except ValueError:
        return jsonify({"error": "NOT_FOUND"}), 404


