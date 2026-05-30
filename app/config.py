"""Estado de configuração em memória do app FinNLP (singleton por processo)."""
from __future__ import annotations
from dataclasses import dataclass, field

# Feeds RSS — ordem define a exibição no UI
RSS_FEEDS: dict[str, str] = {
    "Reuters":        "https://feeds.reuters.com/reuters/businessNews",
    "Financial Times":"https://www.ft.com/rss/home",
    "CNN Brasil":     "https://www.cnnbrasil.com.br/economia/feed/",
    "MarketWatch":    "https://feeds.marketwatch.com/marketwatch/topstories/",
    "Agência Brasil": "https://agenciabrasil.ebc.gov.br/economia/feed",
    "Infomoney":      "https://www.infomoney.com.br/feed/",
    "Valor":          "https://valor.globo.com/rss/home/",
}


@dataclass
class AppState:
    """Configuração mutável compartilhada entre as rotas."""
    interval_minutes: int = 5
    active_model: str = "SVM"          # "SVM" ou "Naive Bayes"
    language: str = "en"               # "en" | "pt" | "auto"
    active_portals: list[str] = field(default_factory=lambda: list(RSS_FEEDS.keys()))
    live_running: bool = False

    def toggle_portal(self, portal: str) -> None:
        if portal in self.active_portals:
            self.active_portals.remove(portal)
        elif portal in RSS_FEEDS:
            self.active_portals.append(portal)


# Singleton de processo
STATE = AppState()
