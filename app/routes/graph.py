"""Grafo de conhecimento: serve edges/centralidade e o HTML interativo PyVis."""
from __future__ import annotations
from pathlib import Path
from flask import Blueprint, jsonify, send_from_directory

bp = Blueprint("graph", __name__)

_PROC = Path(__file__).resolve().parent.parent.parent / "data" / "processed"
_IMG = Path(__file__).resolve().parent.parent.parent / "reports" / "images"


@bp.get("/api/graph")
def graph():
    """Lê o GEXF gerado pelo notebook e devolve nós + centralidade de grau."""
    import networkx as nx
    gexf = _PROC / "grafo_conhecimento.gexf"
    if not gexf.exists():
        return jsonify({"nodes": [], "edges": [], "centrality": {},
                        "message": "Grafo ainda não gerado. Rode o notebook."})
    G = nx.read_gexf(str(gexf))
    centrality = nx.degree_centrality(G)
    top = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:15]
    return jsonify({
        "nodes": list(G.nodes()),
        "edges": [{"source": u, "target": v} for u, v in G.edges()],
        "centrality": {k: round(v, 4) for k, v in top},
        "n_nodes": G.number_of_nodes(),
        "n_edges": G.number_of_edges(),
    })


@bp.get("/api/graph/html")
def graph_html():
    """Serve o HTML interativo do PyVis para embutir em iframe."""
    return send_from_directory(_IMG, "grafo_interativo_r4.html")
