// =============================================================================
// FinNLP — modules.js
// Inicializadores dos módulos: Busca, Grafo, Histórico SCD2, Métricas, Config.
// =============================================================================

window.MODULE_INIT = window.MODULE_INIT || {};

function escM(s) {
  return String(s).replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])
  );
}

// ---- 🔍 Busca Semântica ----------------------------------------------------
window.MODULE_INIT.search = function () {
  const run = async (query) => {
    const out = document.getElementById("search-results");
    if (!query.trim()) return;
    out.innerHTML = `<div class="loading">Buscando…</div>`;
    try {
      const resp = await fetch("/api/search", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, top_n: 5 }),
      });
      const d = await resp.json();
      const rows = (d.results || []);
      out.innerHTML = rows.length
        ? rows.map((r) =>
            `<div class="search-row"><span class="score">${r.score.toFixed(3)}</span>${escM(r.text.slice(0, 160))}…</div>`
          ).join("")
        : '<div class="muted">Nenhum resultado.</div>';
    } catch (e) {
      out.innerHTML = `<div class="error">Erro: ${e}</div>`;
    }
  };

  document.querySelectorAll(".search-preset").forEach((b) =>
    b.addEventListener("click", () => {
      document.getElementById("search-input").value = b.dataset.q;
      run(b.dataset.q);
    })
  );
  const btn = document.getElementById("search-btn");
  if (btn) btn.addEventListener("click", () => run(document.getElementById("search-input").value));
};

// ---- ◉ Grafo de Entidades --------------------------------------------------
window.MODULE_INIT.graph = function () {
  const rank = document.getElementById("centrality-rank");
  if (!rank) return;
  fetch("/api/graph").then((r) => r.json()).then((d) => {
    const cent = d.centrality || {};
    const entries = Object.entries(cent);
    if (!entries.length) {
      rank.innerHTML = `<div class="muted" style="font-size:12px">${escM(d.message || "Grafo ainda não gerado.")}</div>`;
      return;
    }
    const max = entries[0][1] || 1;
    rank.innerHTML = entries.map(([name, val], i) => `
      <div class="sector-row">
        <span class="sector-name" style="width:auto;flex:1">${i + 1}. ${escM(name)}</span>
        <div class="sector-bar" style="max-width:80px"><div class="sector-fill" style="width:${(val / max) * 100}%;background:var(--accent-violet)"></div></div>
        <span class="mono" style="font-size:10px;color:var(--accent-blue-d)">${val.toFixed(3)}</span>
      </div>`).join("") +
      `<div class="muted" style="font-size:11px;margin-top:10px">${d.n_nodes || 0} nós · ${d.n_edges || 0} arestas. Entidades centrais = maior risco de contágio sistêmico.</div>`;
  }).catch((e) => { rank.innerHTML = `<div class="error">Erro: ${e}</div>`; });
};

// ---- 📈 Histórico SCD2 -----------------------------------------------------
window.MODULE_INIT.history = function () {
  const dl = document.getElementById("entities-list");
  fetch("/api/history/entities").then((r) => r.json()).then((d) => {
    if (dl) dl.innerHTML = (d.entities || []).map((e) => `<option value="${escM(e)}">`).join("");
  });

  const run = async () => {
    const ent = document.getElementById("history-input").value.trim();
    const tl = document.getElementById("timeline");
    const tbl = document.getElementById("history-table");
    if (!ent) return;
    tl.innerHTML = `<div class="loading">Consultando…</div>`;
    try {
      const resp = await fetch(`/api/history/${encodeURIComponent(ent)}`);
      const d = await resp.json();
      const hist = d.history || [];
      if (!hist.length) {
        tl.innerHTML = `<div class="muted">Sem histórico registrado para "${escM(ent)}".</div>`;
        tbl.innerHTML = ""; return;
      }
      const color = { positive: "var(--accent-green)", neutral: "var(--accent-yellow)", negative: "var(--accent-red)" };
      tl.innerHTML = `<div style="display:flex;gap:4px;flex-wrap:wrap">` + hist.map((h) =>
        `<div style="flex:1;min-width:80px;background:${color[h.sentimento] || "#888"};border-radius:6px;padding:8px;text-align:center;color:#0A0F1E;font-weight:700;font-size:11px">
           ${escM(h.sentimento)}<br><span style="font-weight:400;font-size:9px">${escM(h.data_inicio || "")}</span></div>`
      ).join("") + `</div>`;
      tbl.innerHTML = `<table class="data-table"><thead><tr><th>Versão</th><th>Sentimento</th><th>Score</th><th>Início</th><th>Fim</th><th>Ativo</th></tr></thead><tbody>` +
        hist.map((h) =>
          `<tr><td>${h.id_versao ?? "—"}</td><td>${escM(h.sentimento)}</td><td>${h.score_centralidade ?? "—"}</td><td>${escM(h.data_inicio || "—")}</td><td>${escM(h.data_fim || "atual")}</td><td>${h.status_ativo ? "✓" : ""}</td></tr>`
        ).join("") + `</tbody></table>`;
    } catch (e) { tl.innerHTML = `<div class="error">Erro: ${e}</div>`; }
  };
  const btn = document.getElementById("history-btn");
  if (btn) btn.addEventListener("click", run);
};

// ---- 📊 Métricas ML --------------------------------------------------------
window.MODULE_INIT.metrics = function () {
  let cache = null;
  const box = document.getElementById("metrics-imgs");
  const show = (cat) => {
    const imgs = (cache && cache.images && cache.images[cat]) || [];
    box.innerHTML = imgs.length
      ? imgs.map((f) => `<img class="metric-img" src="/api/metrics/img/${escM(f)}" alt="${escM(f)}">`).join("")
      : '<div class="muted" style="font-size:13px">Imagens ausentes — execute o notebook (Run All) para gerá-las.</div>';
  };
  fetch("/api/metrics").then((r) => r.json()).then((d) => { cache = d; show("classification"); });
  document.querySelectorAll(".tab").forEach((t) =>
    t.addEventListener("click", () => {
      document.querySelectorAll(".tab").forEach((x) => x.classList.toggle("active", x === t));
      show(t.dataset.cat);
    })
  );
};

// ---- ⚙ Configurações -------------------------------------------------------
window.MODULE_INIT.config = function () {
  const status = document.getElementById("config-status");
  const post = async (body) => {
    await fetch("/api/config", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (status) { status.textContent = "✓ Configuração salva"; setTimeout(() => (status.textContent = ""), 1500); }
  };

  fetch("/api/config").then((r) => r.json()).then((cfg) => {
    // Portais
    const pbox = document.getElementById("config-portals");
    if (pbox) {
      pbox.innerHTML = (cfg.all_portals || []).map((p) => {
        const on = cfg.active_portals.includes(p);
        return `<label class="checkbox-row"><input type="checkbox" data-portal="${escM(p)}" ${on ? "checked" : ""}> ${escM(p)}</label>`;
      }).join("");
      pbox.querySelectorAll("input[data-portal]").forEach((cb) =>
        cb.addEventListener("change", () => post({ toggle_portal: cb.dataset.portal }))
      );
    }
    setVal("config-interval", cfg.interval_minutes);
    setVal("config-model", cfg.active_model);
    setVal("config-lang", cfg.language);
  });

  bindChange("config-interval", (v) => post({ interval_minutes: Number(v) }));
  bindChange("config-model", (v) => post({ active_model: v }));
  bindChange("config-lang", (v) => post({ language: v }));

  function setVal(id, v) { const e = document.getElementById(id); if (e) e.value = v; }
  function bindChange(id, fn) { const e = document.getElementById(id); if (e) e.addEventListener("change", () => fn(e.value)); }
};
