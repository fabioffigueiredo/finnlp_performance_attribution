"""Rotas de páginas: shell principal e fragmentos de módulo (navegação SPA)."""
from __future__ import annotations
from flask import Blueprint, render_template, abort

bp = Blueprint("pages", __name__)

MODULES = {
    "analysis": "_module_analysis.html",
    "search":   "_module_search.html",
    "graph":    "_module_graph.html",
    "history":  "_module_history.html",
    "metrics":  "_module_metrics.html",
    "feed":     "_module_feed.html",
    "live":     "_module_live.html",
    "config":   "_module_config.html",
}


@bp.get("/")
def home():
    # A primeira tela é a análise reproduzível. O módulo SSE continua opcional.
    return render_template("base.html", initial_module="analysis")


@bp.get("/m/<module>")
def module_fragment(module: str):
    template = MODULES.get(module)
    if not template:
        abort(404)
    return render_template(template)
