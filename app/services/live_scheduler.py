"""Agendador em background: busca RSS, classifica e empurra eventos para SSE."""
from __future__ import annotations
import json
import logging
import queue
import threading
import time
from datetime import date
from typing import Any

from app.config import STATE
from app.services.pipeline import PIPELINE
from app.services.rss_scraper import fetch_feeds

_log = logging.getLogger(__name__)


class LiveScheduler:
    """Thread daemon que processa notícias periodicamente e publica em uma fila."""

    def __init__(self) -> None:
        self._queue: queue.Queue[str] = queue.Queue(maxsize=500)
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()
        self._stats = {"positive": 0, "neutral": 0, "negative": 0, "total": 0}

    # ---- controle ----
    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        STATE.live_running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        _log.info("LiveScheduler iniciado.")

    def stop(self) -> None:
        self._stop.set()
        STATE.live_running = False

    # ---- fila SSE ----
    def stream(self):
        """Gerador SSE: bloqueia na fila e formata eventos `data: <json>`."""
        # Envia snapshot de stats ao conectar
        yield self._sse({"type": "stats_update", "data": self._stats})
        while True:
            try:
                payload = self._queue.get(timeout=25)
                yield payload
            except queue.Empty:
                yield ": keep-alive\n\n"  # comentário SSE p/ manter conexão viva

    @staticmethod
    def _sse(obj: dict[str, Any]) -> str:
        return f"data: {json.dumps(obj, ensure_ascii=False)}\n\n"

    def _publish(self, obj: dict[str, Any]) -> None:
        try:
            self._queue.put_nowait(self._sse(obj))
        except queue.Full:
            pass  # descarta se o consumidor está lento

    # ---- loop principal ----
    def _run(self) -> None:
        PIPELINE.warmup()
        while not self._stop.is_set():
            try:
                self._tick()
            except Exception as exc:  # noqa: BLE001
                _log.warning("LiveScheduler tick falhou: %s", exc)
            # Aguarda o intervalo configurado (checando stop a cada 2s)
            waited = 0
            interval_s = max(STATE.interval_minutes, 1) * 60
            while waited < interval_s and not self._stop.is_set():
                time.sleep(2)
                waited += 2

    def _tick(self) -> None:
        news = fetch_feeds(STATE.active_portals, max_per_feed=8)
        for item in news:
            result = PIPELINE.analyze(item["text"], lang="en", top_n=0)
            sentiment = result["sentiment"]
            self._stats[sentiment] = self._stats.get(sentiment, 0) + 1
            self._stats["total"] += 1
            self._persist_scd2(result["entities"], sentiment)
            self._publish({
                "type": "news_item",
                "data": {
                    "title": item["title"],
                    "portal": item["portal"],
                    "link": item["link"],
                    "sentiment": sentiment,
                    "confidence": result["confidence"],
                    "entities": result["entities"][:3],
                },
            })
        self._publish({"type": "stats_update", "data": self._stats})

    def _persist_scd2(self, entities: list[str], sentiment: str) -> None:
        """Versiona o sentimento das entidades no banco SCD2."""
        if not entities:
            return
        try:
            from src.scd2_manager import get_engine, upsert_entity_status
            engine = get_engine()
            for ent in entities:
                upsert_entity_status(engine, ent, sentiment, reference_date=date.today())
        except Exception as exc:  # noqa: BLE001
            _log.warning("SCD2 persist falhou: %s", exc)


# Singleton de processo
SCHEDULER = LiveScheduler()
