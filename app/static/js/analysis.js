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
      document.getElementById("analysis-results").innerHTML = `<div class="analysis-empty"><div class="card-label">Cenário carregado</div><p>Agora execute a análise para chamar o endpoint real. Nenhum resultado é montado antes dessa requisição.</p></div>`;
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
    const originalLabel = btn.textContent;
    btn.disabled = true;
    btn.textContent = "Analisando…";
    out.innerHTML = `<div class="analysis-empty"><div class="card-label">Requisição em andamento</div><p>Chamando <span class="mono">POST /api/analyze</span> e aguardando o retorno do pipeline.</p></div>`;

    try {
      const resp = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, lang, top_n: Number(topN) }),
      });
      const d = await resp.json();
      if (!resp.ok || d.error) throw new Error(d.error || `HTTP ${resp.status}`);
      out.innerHTML = renderAnalysis(d, resp.status);
    } catch (e) {
      out.innerHTML = `<div class="card"><div class="error">Erro na análise: ${escapeHtml(e.message || String(e))}</div></div>`;
    } finally {
      btn.disabled = false;
      btn.textContent = originalLabel;
    }
  });
};

function renderAnalysis(d, httpStatus) {
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

  return `<section class="analysis-result" aria-label="Resultado da análise">
    <div class="result-runbar">
      <div>
        <div class="card-label">Resultado verificável</div>
        <p>Resposta recebida do endpoint real desta demonstração.</p>
      </div>
      <span class="http-status">HTTP ${httpStatus}</span>
    </div>
    <aside class="execution-trace" aria-label="Traço de execução">
      <span class="trace-label">Caminho executado</span>
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
    </div>
  </section>`;
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])
  );
}
