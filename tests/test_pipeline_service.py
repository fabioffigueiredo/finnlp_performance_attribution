import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from app.services.pipeline import PipelineService


@pytest.fixture(scope="module")
def svc():
    s = PipelineService()
    s.warmup()  # carrega corpus + treina modelos uma vez
    return s


def test_analyze_returns_expected_keys(svc):
    result = svc.analyze("Goldman Sachs reported record profit growth this quarter.", lang="en")
    assert set(result.keys()) >= {"sentiment", "confidence", "entities", "topic", "search"}
    assert result["sentiment"] in {"positive", "neutral", "negative"}
    assert isinstance(result["entities"], list)
    assert isinstance(result["search"], list)


def test_search_returns_scored_docs(svc):
    results = svc.search("credit risk default", top_n=3)
    assert len(results) <= 3
    if results:
        assert "score" in results[0] and "text" in results[0]
