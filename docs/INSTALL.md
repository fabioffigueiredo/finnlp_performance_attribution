# Instalação e Configuração — FinNLP

Guia detalhado para preparar o ambiente, com e sem `uv`, e resolver problemas comuns.

---

## Requisitos

| Item | Versão | Observação |
|---|---|---|
| **Python** | **3.12** | 3.13 é incompatível (scipy < 1.14 sem wheels); 3.11 também serve |
| SO | macOS / Linux / Windows | CPU-only, sem GPU |
| Internet | — | Necessária na 1ª execução (download do corpus ~50 MB) |
| Disco | ~1.5 GB | Ambiente virtual + modelos spaCy + corpus |

> O stack é travado em **numpy 1.26.4 + scipy 1.12.0** porque o `gensim 4.3.2`
> usa `scipy.linalg.triu` (removida no scipy 1.13) e quebra com numpy ≥ 2.0.

---

## Opção A — com `uv` (recomendado)

[`uv`](https://docs.astral.sh/uv/) é ~10× mais rápido que pip puro.

```bash
# Instalar uv (caso não tenha)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 1. Ambiente virtual
uv venv .venv --python 3.12
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 2. Dependências (resolve em ~2 min)
uv pip install -r requirements.txt

# 3. Modelos spaCy (via wheel direto)
uv pip install \
  "en-core-web-sm @ https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl" \
  "pt-core-news-sm @ https://github.com/explosion/spacy-models/releases/download/pt_core_news_sm-3.7.0/pt_core_news_sm-3.7.0-py3-none-any.whl"

# 4. Recursos NLTK
python -c "import nltk; [nltk.download(p, quiet=True) for p in ('punkt','punkt_tab','stopwords','rslp')]"
```

> O venv do `uv` não inclui `pip`; use sempre `uv pip install`.

---

## Opção B — com `venv` + `pip` padrão

```bash
# 1. Ambiente virtual
python3.12 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 2. Dependências
pip install --upgrade pip
pip install -r requirements.txt

# 3. Modelos spaCy
python -m spacy download en_core_web_sm
python -m spacy download pt_core_news_sm

# 4. Recursos NLTK
python -c "import nltk; [nltk.download(p, quiet=True) for p in ('punkt','punkt_tab','stopwords','rslp')]"
```

---

## Verificação da instalação

```bash
# Imports principais
python -c "import flask, spacy, sklearn, gensim, networkx, feedparser; print('OK')"

# Modelos spaCy
python -c "import spacy; spacy.load('en_core_web_sm'); spacy.load('pt_core_news_sm'); print('spaCy OK')"

# Factory Flask
PYTHONPATH=. python -c "from app.app import create_app; create_app(); print('factory OK')"

# Suíte de testes
PYTHONPATH=. pytest tests/ -v
```

---

## Executar

```bash
python app/app.py                  # http://localhost:5001
PORT=5002 python app/app.py        # porta alternativa
```

---

## Troubleshooting

| Sintoma | Causa | Solução |
|---|---|---|
| `ModuleNotFoundError: No module named 'app.routes'; 'app' is not a package` | `app/` entrou no `sys.path[0]` e colidiu com o pacote | Já tratado em `app/app.py` (remove o dir do script do path). Rode da raiz. |
| `No module named 'pkg_resources'` | `setuptools ≥ 81` removeu `pkg_resources` (mlflow precisa) | `uv pip install "setuptools<81"` (já no `requirements.txt`) |
| `gensim` / `scipy.linalg.triu` ImportError | numpy 2.x ou scipy ≥ 1.13 | Use as versões fixadas; **Python 3.12**, não 3.13 |
| `No solution found ... gensim ... scipy` (resolver do uv) | Python 3.13 | Recrie o venv com `--python 3.12` |
| `OSError: ... punkt/PY3_tab` | Recursos NLTK ausentes | Rode o passo 4 (download NLTK) |
| `Can't find model 'en_core_web_sm'` | Modelo spaCy não instalado | Rode o passo 3 |
| Análise trava ~1 min | _Warmup_ (download corpus + treino) | Normal na 1ª chamada |
| `Address already in use` | Servidor já rodando na porta | `PORT=5002 python app/app.py` ou encerre o anterior |
| Feeds RSS vazios | Portal indisponível / sem internet | _Skip_ silencioso; verifique portais em ⚙ e a conexão |
| Caminho com espaços/acentos quebra venv nativo | Limitação do `venv` padrão | Prefira `uv`, que lida bem com isso |

---

## Desinstalar / limpar

```bash
deactivate
rm -rf .venv mlruns data/raw/* reports/images/*.tmp
```
