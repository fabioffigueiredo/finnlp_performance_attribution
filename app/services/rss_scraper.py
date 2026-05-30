"""Coleta de notícias via RSS com feedparser. Tolerante a feeds indisponíveis."""
from __future__ import annotations
import logging
import re
from typing import Any

import feedparser

from app.config import RSS_FEEDS

_log = logging.getLogger(__name__)
_HTML = re.compile(r"<[^>]+>")


def _strip_html(text: str) -> str:
    return _HTML.sub(" ", text or "").strip()


def parse_feed_entries(entries: list[dict], portal: str) -> list[dict[str, Any]]:
    """Normaliza entradas de um feed em dicts padronizados. Descarta sem título."""
    out: list[dict] = []
    for e in entries:
        title = _strip_html(e.get("title", ""))
        if not title:
            continue
        summary = _strip_html(e.get("summary", ""))
        out.append({
            "title": title,
            "summary": summary,
            "text": f"{title}. {summary}".strip(),
            "link": e.get("link", ""),
            "portal": portal,
        })
    return out


def fetch_feeds(portals: list[str], max_per_feed: int = 15) -> list[dict[str, Any]]:
    """Busca e parseia os feeds dos portais ativos. Skip silencioso em falha."""
    results: list[dict] = []
    for portal in portals:
        url = RSS_FEEDS.get(portal)
        if not url:
            continue
        try:
            parsed = feedparser.parse(url)
            entries = parsed.entries[:max_per_feed]
            results.extend(parse_feed_entries(entries, portal))
        except Exception as exc:  # noqa: BLE001 — robustez: nunca derruba o app
            _log.warning("Feed '%s' falhou: %s", portal, exc)
    _log.info("RSS: %d notícias de %d portais.", len(results), len(portals))
    return results
