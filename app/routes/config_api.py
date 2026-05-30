"""Leitura e escrita da configuração em memória (AppState)."""
from __future__ import annotations
from flask import Blueprint, request, jsonify

from app.config import STATE, RSS_FEEDS

bp = Blueprint("config", __name__)


@bp.get("/api/config")
def get_config():
    return jsonify({
        "interval_minutes": STATE.interval_minutes,
        "active_model": STATE.active_model,
        "language": STATE.language,
        "active_portals": STATE.active_portals,
        "all_portals": list(RSS_FEEDS.keys()),
        "live_running": STATE.live_running,
    })


@bp.post("/api/config")
def set_config():
    payload = request.get_json(silent=True) or {}
    if "interval_minutes" in payload:
        STATE.interval_minutes = int(payload["interval_minutes"])
    if "active_model" in payload:
        STATE.active_model = str(payload["active_model"])
    if "language" in payload:
        STATE.language = str(payload["language"])
    if "toggle_portal" in payload:
        STATE.toggle_portal(str(payload["toggle_portal"]))
    return get_config()
