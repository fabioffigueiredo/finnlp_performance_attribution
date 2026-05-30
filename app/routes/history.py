"""Histórico SCD2: lista entidades e devolve timeline de sentimento."""
from __future__ import annotations
from flask import Blueprint, jsonify

from src.scd2_manager import get_engine, query_current_status, query_entity_history

bp = Blueprint("history", __name__)


@bp.get("/api/history/entities")
def entities():
    try:
        df = query_current_status(get_engine())
        names = df["nome_entidade"].tolist() if not df.empty else []
    except Exception:  # noqa: BLE001
        names = []
    return jsonify({"entities": names})


@bp.get("/api/history/<path:entity>")
def history(entity: str):
    try:
        df = query_entity_history(get_engine(), entity)
        records = df.to_dict(orient="records") if not df.empty else []
        # Datas → ISO string para JSON
        for r in records:
            for k in ("data_inicio", "data_fim"):
                if r.get(k) is not None:
                    r[k] = str(r[k])
    except Exception:  # noqa: BLE001
        records = []
    return jsonify({"entity": entity, "history": records})
