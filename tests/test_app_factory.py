import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import AppState, RSS_FEEDS


def test_appstate_defaults():
    state = AppState()
    assert state.interval_minutes == 5
    assert state.active_model == "SVM"
    assert state.language == "en"
    # Todos os portais começam ativos
    assert set(state.active_portals) == set(RSS_FEEDS.keys())
    assert state.live_running is False


def test_appstate_toggle_portal():
    state = AppState()
    state.toggle_portal("Reuters")
    assert "Reuters" not in state.active_portals
    state.toggle_portal("Reuters")
    assert "Reuters" in state.active_portals


from app.app import create_app


def test_create_app_registers_routes():
    app = create_app()
    rules = {r.rule for r in app.url_map.iter_rules()}
    assert "/" in rules
    assert "/m/<module>" in rules


def test_home_returns_shell():
    app = create_app()
    client = app.test_client()
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"FinNLP" in resp.data
    assert b"sidebar" in resp.data.lower()
