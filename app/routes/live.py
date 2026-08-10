"""Endpoint SSE opcional + controle explícito do scheduler de demonstração."""
from __future__ import annotations
from flask import Blueprint, request, jsonify, Response, stream_with_context

from app.config import STATE
from app.services.live_scheduler import SCHEDULER

bp = Blueprint("live", __name__)


@bp.get("/stream/live")
def stream():
    # Abrir o canal não é uma autorização para coletar. A ativação ocorre
    # explicitamente em POST /api/live/toggle e o stream apenas transmite o
    # estado da sessão já iniciada pelo usuário.
    return Response(
        stream_with_context(SCHEDULER.stream()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@bp.post("/api/live/toggle")
def toggle():
    action = (request.get_json(silent=True) or {}).get("action", "start")
    if action == "stop":
        SCHEDULER.stop()
    else:
        SCHEDULER.start()
    return jsonify({"live_running": STATE.live_running})
