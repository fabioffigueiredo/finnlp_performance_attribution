# Referência de API — FinNLP

Base URL padrão: `http://localhost:5001`

Todos os endpoints de dados retornam `application/json`, exceto onde indicado.
A primeira chamada que usa o pipeline dispara o _warmup_ (carregamento do corpus +
treino dos modelos, ~30-60s).

---

## Índice

- [Páginas (SPA)](#páginas-spa)
- [Análise](#análise)
- [Busca Semântica](#busca-semântica)
- [Grafo de Conhecimento](#grafo-de-conhecimento)
- [Histórico SCD2](#histórico-scd2)
- [Métricas ML](#métricas-ml)
- [Feed de Notícias](#feed-de-notícias)
- [Mercado Live (SSE)](#mercado-live-sse)
- [Configuração](#configuração)

---

## Páginas (SPA)

### `GET /`
Retorna o _shell_ HTML completo (sidebar + área de conteúdo). O módulo inicial é o
**Mercado Live**.

### `GET /m/<module>`
Retorna o **fragmento HTML** de um módulo (injetado via `fetch` no `#content`).
`module` ∈ `analysis · search · graph · history · metrics · feed · live · config`.

- `200` → fragmento HTML
- `404` → módulo inexistente

---

## Análise

### `POST /api/analyze`
Analisa um texto: sentimento, entidades, tópico LDA e documentos similares.

**Request body:**
```json
{ "text": "Goldman Sachs reported record profit growth.", "lang": "en", "top_n": 3 }
```

| Campo | Tipo | Obrigatório | Padrão | Descrição |
|---|---|:---:|---|---|
| `text` | string | sim | — | Texto a analisar |
| `lang` | string | não | `"en"` | `"en"` ou `"pt"` |
| `top_n` | int | não | `3` | Nº de documentos similares |

**Response `200`:**
```json
{
  "sentiment": "positive",
  "confidence": 0.62,
  "entities": ["Goldman Sachs"],
  "regex": { "monetary": [], "percent": [], "fin_date": [], "ticker": [] },
  "topic": { "id": 3, "terms": ["sale", "profit", "period"], "score": 0.71 },
  "search": [ { "rank": 1, "score": 0.41, "text": "..." } ]
}
```

**Erros:** `400` se `text` vazio (`{"error": "texto vazio"}`).

---

## Busca Semântica

### `POST /api/search`
Retorna os documentos mais similares à consulta (similaridade de cosseno sobre TF-IDF).

**Request body:**
```json
{ "query": "credit risk default", "top_n": 5 }
```

**Response `200`:**
```json
{ "results": [ { "rank": 1, "score": 0.38, "text": "..." } ] }
```

**Erros:** `400` se `query` vazia.

---

## Grafo de Conhecimento

### `GET /api/graph`
Lê o grafo (`data/processed/grafo_conhecimento.gexf`) e retorna nós, arestas e a
centralidade de grau dos 15 nós mais centrais.

**Response `200`:**
```json
{
  "nodes": ["Apple Inc", "Goldman Sachs", "..."],
  "edges": [ { "source": "Apple Inc", "target": "Goldman Sachs" } ],
  "centrality": { "Black & Decker Corporation": 0.0164, "...": 0.0 },
  "n_nodes": 305,
  "n_edges": 315
}
```

Se o grafo ainda não foi gerado: `{ "nodes": [], "edges": [], "centrality": {}, "message": "Grafo ainda não gerado. Rode o notebook." }`

### `GET /api/graph/html`
Retorna o **HTML interativo** do PyVis (`text/html`), para embutir em `<iframe>`.

---

## Histórico SCD2

### `GET /api/history/entities`
Lista as entidades com registro ativo no banco SCD2.

**Response `200`:** `{ "entities": ["Apple Inc", "Goldman Sachs"] }`

### `GET /api/history/<entity>`
Retorna o histórico completo de versões de sentimento de uma entidade.

**Response `200`:**
```json
{
  "entity": "Apple Inc",
  "history": [
    { "id_versao": 1, "sentimento": "positive", "score_centralidade": 0.45,
      "data_inicio": "2026-05-01", "data_fim": "2026-05-30", "status_ativo": false },
    { "id_versao": 4, "sentimento": "negative", "score_centralidade": 0.45,
      "data_inicio": "2026-05-30", "data_fim": null, "status_ativo": true }
  ]
}
```

Entidade sem histórico → `{ "entity": "...", "history": [] }`.

---

## Métricas ML

### `GET /api/metrics`
Lista as imagens de métricas disponíveis (geradas pelo notebook), por categoria.

**Response `200`:**
```json
{ "images": {
    "classification": ["confusion_matrix_SVM_LinearSVC.png", "classifier_comparison.png"],
    "topics": ["lda_topics_r3.png"],
    "embeddings": ["tsne_r2.png", "tfidf_heatmap_r2.png"]
} }
```

### `GET /api/metrics/img/<filename>`
Serve uma imagem de `reports/images/` (`image/png`).

---

## Feed de Notícias

### `POST /api/feed/fetch`
Coleta notícias via RSS dos portais informados (ou os ativos por padrão), classifica
cada uma e retorna a lista.

**Request body:** `{ "portals": ["Reuters", "Infomoney"] }` _(opcional — usa os ativos se omitido)_

**Response `200`:**
```json
{
  "count": 8,
  "news": [
    { "title": "Goldman Sachs beats Q2 estimates", "portal": "Reuters",
      "link": "https://...", "sentiment": "positive", "confidence": 0.91,
      "entities": ["Goldman Sachs"] }
  ]
}
```

---

## Mercado Live (SSE)

### `GET /stream/live`
Abre um stream **Server-Sent Events** (`text/event-stream`). Inicia o `LiveScheduler`
se ainda não estiver rodando. O cliente conecta com `new EventSource("/stream/live")`.

**Eventos emitidos** (cada um em uma linha `data: <json>`):

```
data: {"type": "stats_update", "data": {"positive": 12, "neutral": 4, "negative": 2, "total": 18}}

data: {"type": "news_item", "data": {"title": "...", "portal": "Reuters", "link": "...",
       "sentiment": "positive", "confidence": 0.84, "entities": ["Apple Inc"]}}
```

Linhas `: keep-alive` são enviadas periodicamente para manter a conexão viva.

### `POST /api/live/toggle`
Inicia ou para o scheduler de coleta.

**Request body:** `{ "action": "start" }` ou `{ "action": "stop" }`
**Response `200`:** `{ "live_running": true }`

---

## Configuração

### `GET /api/config`
Estado atual da configuração em memória.

**Response `200`:**
```json
{
  "interval_minutes": 5,
  "active_model": "SVM",
  "language": "en",
  "active_portals": ["Reuters", "Financial Times", "..."],
  "all_portals": ["Reuters", "Financial Times", "CNN Brasil", "MarketWatch",
                  "Agência Brasil", "Infomoney", "Valor"],
  "live_running": false
}
```

### `POST /api/config`
Atualiza campos da configuração (todos opcionais; envie só o que mudar).

| Campo | Tipo | Efeito |
|---|---|---|
| `interval_minutes` | int | Intervalo de coleta do Live |
| `active_model` | string | `"SVM"` ou `"Naive Bayes"` |
| `language` | string | `"en"`, `"pt"` ou `"auto"` |
| `toggle_portal` | string | Liga/desliga um portal (ex: `"Reuters"`) |

**Response `200`:** o objeto de configuração completo e atualizado (mesmo shape do `GET`).
