# FinNLP — Pipeline de Monitoramento e Inteligência do Mercado Financeiro

> **Projeto de Disciplina (PD1) — Processamento de Linguagem Natural**
> Pós-Graduação em Machine Learning, Deep Learning e Inteligência Artificial — INFNET
> **Autor:** Fabio Ferreira Figueiredo

Pipeline _end-to-end_ de PLN que transforma notícias e relatórios financeiros
brutos em inteligência acionável para a **Diretoria de Estratégia de um fundo de
investimentos**: classificação de sentimento (Risco/Oportunidade), modelagem de
tópicos latentes, busca semântica e um grafo de conhecimento com versionamento
histórico (SCD Tipo 2) para suportar análises de _performance attribution_.

> **Nota de contexto:** Este é um projeto **acadêmico**. O cliente ("Gestão do
> Fundo") é **fictício e genérico**. Nenhuma instituição financeira real está
> envolvida ou referenciada.

> **Nota de compliance / anonimização:** Os dados utilizados são públicos
> (corpus aberto) e/ou **sintéticos**. Quaisquer trechos derivados de fontes
> corporativas foram **anonimizados** — nomes, identificadores e valores
> sensíveis foram substituídos por equivalentes fictícios antes de qualquer
> processamento.

---

## 🎯 Cobertura das Rubricas (INFNET)

| Rubrica | Onde é atendida |
|---|---|
| **1. Pré-processamento** (NLTK + spaCy, lematização vs stemming, POS, WordCloud) | `src/coleta_preprocessamento.py` · Notebook Fase 1 |
| **2. Representação vetorial + busca** (TF-IDF, Word2Vec, cosseno, t-SNE) | `src/modelagem_vetorizacao.py` · Notebook Fase 2 |
| **3. Modelagem** (Naive Bayes vs SVM, F1, LDA + pyLDAvis, MLflow) | `src/modelagem_vetorizacao.py` · Notebook Fase 3 |
| **4. NER + Grafo + SCD2** (spaCy ORG, Levenshtein, NetworkX, SQLAlchemy) | `src/ner_grafo.py` · `src/scd2_manager.py` · Notebook Fase 4 |
| **5. Comunicação** (síntese executiva, app web, relatório) | `app/` (Flask) · `reports/` · Notebook Fase 5 |

---

## 📂 Estrutura do Repositório (padrão MLOps)

```
PD1/
├── data/
│   ├── raw/          # Corpus bruto coletado / baixado
│   ├── processed/    # Corpus pré-processado (lematizado)
│   └── db/           # Banco SQLite do SCD Tipo 2
├── notebooks/        # FinNLP_Pipeline.ipynb (end-to-end, acadêmico)
├── src/              # Módulos Python reutilizáveis do pipeline
│   ├── coleta_preprocessamento.py   # Fases 0 e 1
│   ├── modelagem_vetorizacao.py     # Fases 2 e 3
│   ├── ner_grafo.py                 # Fase 4 (NER + grafo)
│   └── scd2_manager.py              # Fase 4 (engenharia de dados SCD2)
├── app/              # Frontend web (Flask + Vanilla JS + SSE)
│   ├── app.py        # Application factory
│   ├── config.py     # AppState (portais, intervalo, modelo)
│   ├── routes/       # Blueprints: pages + 8 endpoints de API
│   ├── services/     # pipeline · rss_scraper · live_scheduler
│   ├── templates/    # base.html (shell) + 8 fragmentos de módulo
│   └── static/       # css/ (Dark Financial) + js/ (SPA, SSE) + img/
├── reports/          # Relatório técnico (PDF) + imagens geradas
│   └── images/       # Visualizações + grafo interativo (HTML)
├── tests/            # Testes automatizados (16 testes)
├── requirements.txt  # Dependências fixadas
└── README.md
```

---

## ⚙️ Como Reproduzir

> Ambiente recomendado: **Python 3.12** (CPU-only, sem GPU).
> Gerenciador recomendado: **uv** (10× mais rápido que pip puro).

```bash
# 1. Instalar uv (caso não tenha)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Ambiente virtual com Python 3.12
uv venv .venv --python 3.12
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 3. Dependências (uv resolve e instala em ~2 min)
uv pip install -r requirements.txt

# 4. Modelos de linguagem do spaCy
uv pip install \
  "en-core-web-sm @ https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl" \
  "pt-core-news-sm @ https://github.com/explosion/spacy-models/releases/download/pt_core_news_sm-3.7.0/pt_core_news_sm-3.7.0-py3-none-any.whl"

# 5. Notebook end-to-end
jupyter notebook notebooks/FinNLP_Pipeline.ipynb

# 6. (Opcional) UI de tracking de experimentos
mlflow ui

# 7. (Opcional) Aplicativo web de inferência e monitoramento
python app/app.py        # acesse http://localhost:5001
```

> **Sem uv?** Use `python3.12 -m venv .venv` + `pip install -r requirements.txt`
> e depois `python -m spacy download en_core_web_sm pt_core_news_sm`.

---

## 🖥️ Aplicação Web (FinNLP Intelligence Platform)

Frontend premium (estética **Dark Financial**) com 8 módulos e monitoramento de
mercado em tempo real. Construído em **Flask + Vanilla JS + SSE** — sem npm, sem
build pipeline.

```bash
python app/app.py
# Acesse http://localhost:5001
```

**Módulos disponíveis:**

| Módulo | Função |
|---|---|
| ⚡ **Análise de Texto** | Cola uma notícia → sentimento + entidades (NER) + tópico LDA + busca semântica |
| 🔍 **Busca Semântica** | Motor de cosseno com 3 queries de performance attribution + consulta livre |
| ◉ **Grafo de Entidades** | Grafo interativo (PyVis) + ranking de centralidade / risco de contágio |
| 📈 **Histórico SCD2** | Linha do tempo do sentimento de cada entidade (versionamento temporal) |
| 📊 **Métricas ML** | Matrizes de confusão NB vs SVM, tópicos LDA, embeddings t-SNE |
| 📡 **Feed de Notícias** | Scraping RSS manual dos portais selecionados, classificado |
| 🌐 **Mercado Live** | Sentimento agregado + stream de notícias em tempo real (SSE) |
| ⚙ **Configurações** | Portais RSS ativos, intervalo de coleta, modelo e idioma |

**Arquitetura:** os módulos `src/` (NLP) são encapsulados por `app/services/`
(lazy-load dos modelos). As notícias chegam via RSS (`feedparser`) de Reuters,
Financial Times, CNN Brasil, MarketWatch, Agência Brasil, Infomoney e Valor.
O *Mercado Live* usa **Server-Sent Events** para push contínuo sem recarregar a
página.

> A primeira análise dispara o *warmup* (carrega o corpus + treina os modelos),
> levando ~30-60s. Requisições seguintes são instantâneas.

---

## 🧭 Padrões de Engenharia adotados

- **Complexidade ciclomática** estritamente **< 10** por função (Princípio da
  Responsabilidade Única / SOLID).
- **Duplicação de código < 5%** (DRY) — lógica centralizada em `src/`.
- **Reprodutibilidade**: `random_state=42` em todas as etapas estocásticas.
- **Narrativa em 1ª pessoa** nas docstrings e células Markdown, documentando as
  decisões técnicas tomadas.
