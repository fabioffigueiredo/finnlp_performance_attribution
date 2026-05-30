"""Application Factory do FinNLP Frontend."""
from __future__ import annotations
import os
import sys
from pathlib import Path

# Bootstrap de path: ao rodar `python app/app.py`, o Python coloca o diretório
# `app/` em sys.path[0], fazendo `import app` resolver para este próprio arquivo
# (app.py) em vez do pacote `app/`. Removemos o diretório do script e garantimos
# a raiz do projeto na frente, para que `from app.routes...` resolva o pacote.
_HERE = Path(__file__).resolve().parent          # .../PD1/app
_ROOT = _HERE.parent                              # .../PD1
sys.path[:] = [p for p in sys.path if Path(p).resolve() != _HERE]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from flask import Flask


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )

    from app.routes.pages import bp as pages_bp
    from app.routes.analysis import bp as analysis_bp
    from app.routes.search import bp as search_bp
    from app.routes.graph import bp as graph_bp
    from app.routes.history import bp as history_bp
    from app.routes.metrics import bp as metrics_bp
    from app.routes.feed import bp as feed_bp
    from app.routes.live import bp as live_bp
    from app.routes.config_api import bp as config_bp

    for bp in (pages_bp, analysis_bp, search_bp, graph_bp, history_bp,
               metrics_bp, feed_bp, live_bp, config_bp):
        app.register_blueprint(bp)

    return app


if __name__ == "__main__":
    application = create_app()
    port = int(os.environ.get("PORT", 5001))
    print(f"\n  FinNLP rodando em http://localhost:{port}\n")
    # use_reloader=False: o reloader do Werkzeug re-executa o script e quebra
    # o import do pacote `app` quando rodado como `python app/app.py`.
    application.run(host="127.0.0.1", port=port, debug=True,
                    threaded=True, use_reloader=False)
