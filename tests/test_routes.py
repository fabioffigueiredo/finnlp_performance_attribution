import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from app.app import create_app


@pytest.fixture(scope="module")
def client():
    return create_app().test_client()


def test_analyze_endpoint(client):
    resp = client.post("/api/analyze", json={
        "text": "Goldman Sachs reported record profit growth.",
        "lang": "en", "top_n": 3,
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert "sentiment" in data
    assert "entities" in data
    assert "topic" in data


def test_search_endpoint(client):
    resp = client.post("/api/search", json={"query": "credit risk", "top_n": 3})
    assert resp.status_code == 200
    assert isinstance(resp.get_json().get("results"), list)


def test_config_get_and_post(client):
    resp = client.get("/api/config")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "active_portals" in data and "interval_minutes" in data

    resp2 = client.post("/api/config", json={"interval_minutes": 15})
    assert resp2.status_code == 200
    assert resp2.get_json()["interval_minutes"] == 15


def test_metrics_endpoint(client):
    resp = client.get("/api/metrics")
    assert resp.status_code == 200
    assert "images" in resp.get_json()


def test_graph_endpoint(client):
    resp = client.get("/api/graph")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "nodes" in data and "centrality" in data


def test_history_entities_endpoint(client):
    resp = client.get("/api/history/entities")
    assert resp.status_code == 200
    assert isinstance(resp.get_json().get("entities"), list)


def test_feed_fetch_endpoint(client, monkeypatch):
    import app.routes.feed as feed_mod
    monkeypatch.setattr(feed_mod, "fetch_feeds", lambda portals, max_per_feed=8: [
        {"title": "Test news", "text": "Test news. body", "link": "http://x",
         "portal": "Reuters", "summary": "body"},
    ])
    resp = client.post("/api/feed/fetch", json={"portals": ["Reuters"]})
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data["news"]) == 1
    assert data["news"][0]["sentiment"] in {"positive", "neutral", "negative"}


def test_live_toggle_endpoint(client):
    resp = client.post("/api/live/toggle", json={"action": "stop"})
    assert resp.status_code == 200
    assert "live_running" in resp.get_json()


def test_live_stream_headers(client):
    from app.config import STATE
    from app.services.live_scheduler import SCHEDULER

    SCHEDULER.stop()
    resp = client.get("/stream/live", buffered=False)
    assert resp.status_code == 200
    assert resp.headers["Content-Type"].startswith("text/event-stream")
    assert STATE.live_running is False
    resp.close()
