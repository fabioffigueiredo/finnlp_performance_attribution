"""Scraping RSS manual: busca, classifica e devolve notícias."""
from __future__ import annotations
from flask import Blueprint, request, jsonify

from app.config import STATE
from app.services.pipeline import PIPELINE
from app.services.rss_scraper import fetch_feeds

bp = Blueprint("feed", __name__)


@bp.post("/api/feed/fetch")
def fetch():
    payload = request.get_json(silent=True) or {}
    portals = payload.get("portals") or STATE.active_portals
    raw = fetch_feeds(portals, max_per_feed=8)
    news = []
    for item in raw:
        result = PIPELINE.analyze(item["text"], lang="en", top_n=0)
        news.append({
            "title": item["title"],
            "portal": item["portal"],
            "link": item["link"],
            "sentiment": result["sentiment"],
            "confidence": result["confidence"],
            "entities": result["entities"][:3],
        })
    return jsonify({"news": news, "count": len(news)})
