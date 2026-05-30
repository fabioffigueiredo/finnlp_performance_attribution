"""Motor de busca semântica por similaridade de cosseno."""
from __future__ import annotations
from flask import Blueprint, request, jsonify

from app.services.pipeline import PIPELINE

bp = Blueprint("search", __name__)


@bp.post("/api/search")
def search():
    payload = request.get_json(silent=True) or {}
    query = (payload.get("query") or "").strip()
    if not query:
        return jsonify({"error": "query vazia"}), 400
    top_n = int(payload.get("top_n", 3))
    return jsonify({"results": PIPELINE.search(query, top_n=top_n)})
