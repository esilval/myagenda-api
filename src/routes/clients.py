from __future__ import annotations

from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from src.database import get_db
from src.dto.client_dto import ClientCreateDTO, ClientStatus
from src.services.client_service import ClientService
from src.utils.auth import require_auth
from flask import g


bp = Blueprint("clients", __name__, url_prefix="/clients")


@bp.post("")
@require_auth
def create_client():
    try:
        dto = ClientCreateDTO(**request.get_json(force=True))
    except ValidationError as e:
        return jsonify({"error": [err.get("msg") for err in e.errors()]}), 400
    db = next(get_db())
    try:
        service = ClientService(db)
        c = service.create(dto, current_user_id=g.current_user.id)
        return jsonify(c.model_dump()), 201
    except ValueError as e:
        if str(e) in {"EMAIL_TAKEN", "PHONE_TAKEN"}:
            return jsonify({"error": str(e)}), 409
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()


@bp.get("")
@require_auth
def list_clients():
    page = int(request.args.get("page", 1))
    size = int(request.args.get("size", 10))
    status = request.args.get("status")
    text = request.args.get("q")
    include_company = request.args.get("include_company") == "true"
    status_enum = ClientStatus(status) if status in {"ACTIVE", "INACTIVE"} else None
    db = next(get_db())
    try:
        service = ClientService(db)
        total, items = service.list_paginated(page=page, size=size, status=status_enum, text=text, current_user_id=g.current_user.id)
        result = [i.model_dump() for i in items]
        if include_company:
            # naive join: fetch companies by batch
            from src.dao.company_dao import CompanyDAO

            company_ids = {it["company_id"] for it in result if it.get("company_id")}
            companies = {c.id: c for c in CompanyDAO(db).get_by_ids(list(company_ids))}
            for it in result:
                cid = it.get("company_id")
                comp = companies.get(cid)
                if comp:
                    it["company"] = {
                        "id": comp.id,
                        "nit": comp.nit,
                        "business_name": comp.business_name,
                        "city": comp.city,
                        "status": comp.status.value,
                    }
        return jsonify({"total": total, "items": result}), 200
    finally:
        db.close()


@bp.put("/<client_id>")
@require_auth
def update_client(client_id: str):
    try:
        dto = ClientCreateDTO(**request.get_json(force=True))
    except ValidationError as e:
        return jsonify({"error": [err.get("msg") for err in e.errors()]}), 400
    db = next(get_db())
    try:
        c = ClientService(db).update(client_id, dto)
        return jsonify(c.model_dump()), 200
    except ValueError as e:
        if str(e) == "NOT_FOUND":
            return jsonify({"error": "NOT_FOUND"}), 404
        if str(e) in {"EMAIL_TAKEN", "PHONE_TAKEN"}:
            return jsonify({"error": str(e)}), 409
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()


@bp.post("/<client_id>/deactivate")
@require_auth
def deactivate_client(client_id: str):
    db = next(get_db())
    try:
        c = ClientService(db).deactivate(client_id)
        return jsonify(c.model_dump()), 200
    except ValueError as e:
        code = 404 if str(e) == "NOT_FOUND" else 400
        return jsonify({"error": str(e)}), code
    finally:
        db.close()


@bp.delete("/<client_id>")
@require_auth
def delete_client(client_id: str):
    db = next(get_db())
    try:
        ClientService(db).delete(client_id)
        return ("", 204)
    except ValueError as e:
        code = 404 if str(e) == "NOT_FOUND" else 400
        return jsonify({"error": str(e)}), code
    finally:
        db.close()


