"""Rota de análise de texto: sentimento + NER + tópico + busca."""
from __future__ import annotations
from flask import Blueprint, request, jsonify

from app.services.pipeline import PIPELINE

bp = Blueprint("analysis", __name__)


@bp.post("/api/analyze")
def analyze():
    payload = request.get_json(silent=True) or {}
    text = (payload.get("text") or "").strip()
    if not text:
        return jsonify({"error": "texto vazio"}), 400
    lang = payload.get("lang", "en")
    top_n = int(payload.get("top_n", 3))
    result = PIPELINE.analyze(text, lang=lang, top_n=top_n)
    return jsonify(result)
