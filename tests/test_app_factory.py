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


def test_home_opens_a_safe_analysis_demo_not_a_live_claim():
    """A pessoa que abre o projeto começa no fluxo gravável e não em um feed simulado."""
    app = create_app()
    client = app.test_client()
    resp = client.get("/")

    assert resp.status_code == 200
    assert b'data-initial="analysis"' in resp.data
    assert b"scope-badge" in resp.data
    assert b"AO VIVO" not in resp.data


def test_analysis_fragment_exposes_a_labeled_demo_and_limits():
    """O cenário é visível no mesmo limite público que será gravado."""
    app = create_app()
    client = app.test_client()
    resp = client.get("/m/analysis")

    assert resp.status_code == 200
    assert b'id="load-demo-scenario"' in resp.data
    assert "dados públicos/sintéticos".encode() in resp.data
    assert "não é recomendação de investimento".encode() in resp.data


def test_analysis_fragment_exposes_an_inspectable_demo_contract():
    """A primeira tela explica o que é verificável sem simular produção."""
    app = create_app()
    client = app.test_client()
    resp = client.get("/m/analysis")

    assert resp.status_code == 200
    assert b'analysis-hero' in resp.data
    assert b'POST /api/analyze' in resp.data
    assert "PipelineService".encode() in resp.data
    assert "resultado verificável".encode() in resp.data


def test_optional_collection_modules_expose_manual_scope_before_any_request():
    """Módulos auxiliares não devem parecer produção nem iniciar por padrão."""
    app = create_app()
    client = app.test_client()

    live = client.get("/m/live")
    feed = client.get("/m/feed")

    assert live.status_code == 200
    assert "Modo de demonstração".encode() in live.data
    assert "Iniciar demonstração".encode() in live.data
    assert "Nenhuma sessão iniciada".encode() in live.data
    assert "monitoramento contínuo".encode() in live.data
    assert feed.status_code == 200
    assert "Execução sob demanda".encode() in feed.data
    assert "Executar coleta".encode() in feed.data
