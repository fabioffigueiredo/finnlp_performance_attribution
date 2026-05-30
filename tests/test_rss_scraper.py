import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.rss_scraper import parse_feed_entries


def test_parse_feed_entries_normalizes():
    fake_entries = [
        {"title": "Apple beats estimates", "summary": "Strong Q2 results", "link": "http://x/1"},
        {"title": "", "summary": "no title here", "link": "http://x/2"},  # descartado
    ]
    out = parse_feed_entries(fake_entries, portal="Reuters")
    assert len(out) == 1
    item = out[0]
    assert item["title"] == "Apple beats estimates"
    assert item["portal"] == "Reuters"
    assert item["text"]  # texto não-vazio (title + summary)
    assert "link" in item
