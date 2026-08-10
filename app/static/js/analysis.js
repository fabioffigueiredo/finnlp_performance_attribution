// =============================================================================
// FinNLP — analysis.js
// Módulo ⚡ Análise de Texto: POST /api/analyze e renderização dos 4 cards.
// =============================================================================

window.MODULE_INIT = window.MODULE_INIT || {};

window.MODULE_INIT.analysis = function () {
  const btn = document.getElementById("analyze-btn");
  if (!btn) return;
  const scenario = document.getElementById("load-demo-scenario");
  const demoText = "Demo Corporation reported strong quarterly earnings and a higher operating margin. This is a fictional public demonstration scenario.";

  if (scenario) {
    scenario.addEventListener("click", () => {
      document.getElementById("analyze-text").value = demoText;
      document.getElementById("analyze-lang").value = "en";
      document.getElementById("analyze-topn").value = "3";
      document.getElementById("analysis-results").innerHTML = `<div class="card"><div class="muted" style="font-size:13px">Cenário carregado. Clique em Analisar para executar o endpoint real.</div></div>`;
    });
  }

  btn.addEventListener("click", async () => {
    const text = document.getElementById("analyze-text").value.trim();
    const lang = document.getElementById("analyze-lang").value;
    const topN = document.getElementById("analyze-topn").value;
    const out = document.getElementById("analysis-results");
    if (!text) {
      out.innerHTML = `<div class="card"><div class="error">Cole um texto para analisar.</div></div>`;
      return;
    }
    out.innerHTML = `<div class="card"><div class="loading">Analisando…</div></div>`;

    try {
      const resp = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, lang, top_n: Number(topN) }),
      });
      const d = await resp.json();
      if (d.error) throw new Error(d.error);
      out.innerHTML = renderAnalysis(d);
    } catch (e) {
      out.innerHTML = `<div class="card"><div class="error">Erro na análise: ${e}</div></div>`;
    }
  });
};

function renderAnalysis(d) {
  const sentClass = { positive: "pos", neutral: "neu", negative: "neg" }[d.sentiment] || "neu";
  const conf = Math.round((d.confidence || 0) * 100);
  const ents = (d.entities || []).length
    ? d.entities.map((e) => `<span class="entity-tag">${escapeHtml(e)}</span>`).join(" ")
    : '<span class="muted">Nenhuma organização detectada</span>';
  const terms = (d.topic && d.topic.terms || []).join(", ");
  const search = (d.search || []).length
    ? d.search.map((s) =>
        `<div class="search-row"><span class="score">${s.score.toFixed(3)}</span>${escapeHtml(s.text.slice(0, 110))}…</div>`
      ).join("")
    : '<span class="muted">—</span>';

  return `
    <aside class="execution-trace" aria-label="Traço de execução">
      <span class="trace-label">Execução verificada</span>
      <span class="mono">POST /api/analyze</span><span aria-hidden="true">→</span>
      <span class="mono">PipelineService</span><span aria-hidden="true">→</span>
      <span>resultado</span>
    </aside>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px">
      <div class="result-card">
        <div class="card-label">Sentimento</div>
        <span class="sentiment-badge ${sentClass}" style="font-size:13px">${d.sentiment.toUpperCase()} · ${conf}%</span>
      </div>
      <div class="result-card">
        <div class="card-label">Tópico LDA</div>
        <div class="topic-val">Tópico ${d.topic ? d.topic.id : "—"}</div>
        <div class="topic-terms">${escapeHtml(terms)}</div>
      </div>
    </div>
    <div class="result-card" style="margin-bottom:12px">
      <div class="card-label">Entidades (ORG, pós-Levenshtein)</div>
      <div style="display:flex;gap:4px;flex-wrap:wrap">${ents}</div>
    </div>
    <div class="result-card">
      <div class="card-label">Busca Semântica (cosseno)</div>
      ${search}
    </div>`;
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])
  );
}
