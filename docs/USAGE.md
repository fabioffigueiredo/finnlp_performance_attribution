# Guia de Uso — FinNLP

Como usar cada um dos 8 módulos da plataforma. Inicie com `python app/app.py` e acesse
`http://localhost:5001`. A navegação é feita pelo **sidebar** à esquerda (sem recarregar a página).

> **Primeira vez:** a primeira análise carrega o corpus e treina os modelos (~30-60s).
> A barra de status do sidebar mostra o modelo ativo e o estado do scraper.

---

## ⚡ Análise de Texto

O módulo central de inferência sob demanda.

1. Cole uma notícia financeira no campo de texto (ex.: _"Goldman Sachs reported record
   profit growth this quarter, beating estimates."_).
2. Escolha o **idioma** (EN/PT) e o **Top-N** de documentos similares (1–10).
3. Clique em **⚡ Analisar**.

**Resultado (4 cartões):**

| Cartão | Conteúdo |
|---|---|
| **Sentimento** | Classe (Positivo/Neutro/Negativo) + confiança em % |
| **Tópico LDA** | Tópico dominante + termos característicos |
| **Entidades ORG** | Organizações extraídas e normalizadas (Levenshtein) |
| **Busca Semântica** | Documentos do corpus mais próximos, com score de cosseno |

💡 _Dica:_ textos em inglês têm melhor precisão (o classificador é treinado no
`financial_phrasebank`, em inglês).

---

## 🔍 Busca Semântica

Recupera os documentos do corpus mais semanticamente próximos de uma consulta.

- Clique em uma das **3 consultas pré-definidas** de performance attribution:
  - 💱 Impacto cambial no varejo
  - ⚠️ Risco de crédito soberano
  - 📈 Crescimento em tech
- Ou digite uma **consulta livre** e clique em **Buscar**.

Cada resultado mostra o **score de cosseno** (0–1; quanto maior, mais similar) e um trecho
do documento. Útil para encontrar precedentes históricos de um tema de mercado.

---

## ◉ Grafo de Entidades

Visualiza a rede de coocorrência entre organizações citadas no corpus.

- O **grafo interativo** (PyVis) permite _zoom_, arrastar nós e _hover_ para detalhes.
- À direita, o **ranking de centralidade de grau** (Top 15): entidades mais centrais são
  os _hubs_ de maior **risco de contágio sistêmico** — uma notícia negativa sobre elas
  tende a se propagar para múltiplos ativos conectados.

> Requer que o grafo tenha sido gerado pelo notebook
> (`data/processed/grafo_conhecimento.gexf`). Se vazio, rode o notebook.

---

## 📈 Histórico SCD2

Mostra como o sentimento de uma entidade **evoluiu ao longo do tempo** (Slowly Changing
Dimension Tipo 2).

1. Digite/selecione uma entidade (autocompletar lista as entidades do banco).
2. Clique em **Consultar**.

**Resultado:**
- **Linha do tempo** colorida por sentimento (verde/amarelo/vermelho), uma faixa por versão.
- **Tabela de versões** com `data_inicio`, `data_fim` e qual está ativa.

Cada mudança de sentimento fecha a versão anterior (`data_fim`) e abre uma nova —
permitindo _"time travel"_ e backtesting de teses de investimento.

---

## 📊 Métricas ML

Galeria das visualizações geradas pelo pipeline, em 3 abas:

| Aba | Conteúdo |
|---|---|
| **Classificação** | Matrizes de confusão (SVM e Naive Bayes) + comparação F1/Precision/Recall |
| **Tópicos LDA** | Top termos por tópico latente |
| **Embeddings** | Projeção t-SNE do Word2Vec + heatmap TF-IDF |

> As imagens vêm de `reports/images/` (geradas pelo notebook). Execute o notebook
> (Run All) se estiverem ausentes.

---

## 📡 Feed de Notícias

Coleta RSS **sob demanda** (diferente do Live, que é contínuo).

1. Selecione os **portais** desejados (chips no topo — clique para ligar/desligar).
2. Clique em **🔄 Buscar agora**.

Cada notícia coletada é classificada na hora e exibida com badge de sentimento, portal de
origem e entidades extraídas. Bom para uma varredura pontual do noticiário atual.

---

## 🌐 Mercado Live

O painel de **monitoramento em tempo real** — o módulo principal.

**Ao abrir**, conecta automaticamente ao stream SSE. A barra de status mostra
`● Conectado`.

- **Gauges (topo):** sentimento geral (% positivo), notícias processadas, risco
  detectado (% negativo) e status do stream.
- **Stream ao vivo:** cada notícia coletada aparece no topo da lista, classificada, em
  tempo real — sem recarregar a página.
- **Controles:** seletor de **intervalo** de coleta (5/15/30/60 min), **⏸ Pausar** (fecha
  o stream) e **▶ Retomar**.
- **Chips de portal:** ligam/desligam fontes que alimentam o stream.

Por baixo, o scheduler coleta os feeds no intervalo configurado, classifica cada notícia,
**persiste o sentimento no banco SCD2** e empurra os eventos para o navegador.

---

## ⚙ Configurações

Controle central do comportamento da plataforma:

- **Portais RSS:** habilite/desabilite cada fonte (Reuters, Financial Times, CNN Brasil,
  MarketWatch, Agência Brasil, Infomoney, Valor).
- **Coleta automática:** intervalo de atualização do Mercado Live.
- **Modelo & Idioma:** modelo de classificação ativo (SVM / Naive Bayes) e idioma padrão.

As alterações são aplicadas imediatamente e refletidas nos demais módulos.

---

## Fluxo de trabalho sugerido

```
1. Configurações (⚙)  → escolher portais e intervalo
2. Mercado Live (🌐)   → deixar monitorando o sentimento agregado
3. Análise (⚡)         → investigar uma notícia específica em profundidade
4. Grafo (◉)           → ver quem é hub de contágio
5. Histórico (📈)       → checar a evolução do sentimento de um ativo
```
