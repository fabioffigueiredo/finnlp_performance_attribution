// =============================================================================
// FinNLP — live.js
// Módulos opcionais: Stream SSE explícito + coleta manual de fontes RSS públicas.
// =============================================================================

window.MODULE_INIT = window.MODULE_INIT || {};

let _es = null;

// ---- Stream SSE de demonstração -------------------------------------------
window.MODULE_INIT.live = function () {
  const stream = document.getElementById("news-stream");
  if (!stream) return;

  renderPortalChips("live-portals", "live");

  const pause = document.getElementById("live-pause");
  const resume = document.getElementById("live-resume");
  const status = document.getElementById("gauge-status");

  if (resume) resume.addEventListener("click", async () => {
    resume.disabled = true;
    resume.textContent = "Iniciando…";
    try {
      await setLiveState("start");
      connectSSE(stream);
      resume.textContent = "Demonstração em andamento";
      if (pause) pause.disabled = false;
    } catch (error) {
      resume.disabled = false;
      resume.textContent = "Iniciar demonstração";
      if (status) {
        status.textContent = "Falha ao iniciar";
        status.style.color = "var(--accent-red)";
      }
    }
  });
  if (pause) pause.addEventListener("click", async () => {
    pause.disabled = true;
    if (_es) { _es.close(); _es = null; }
    try { await setLiveState("stop"); } catch { /* estado visual continua seguro */ }
    if (status) { status.textContent = "Pausado"; status.style.color = "var(--text-muted)"; }
    if (resume) {
      resume.disabled = false;
      resume.textContent = "Retomar demonstração";
    }
  });

  const interval = document.getElementById("live-interval");
  if (interval) interval.addEventListener("change", () => {
    fetch("/api/config", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ interval_minutes: Number(interval.value) }),
    });
  });
};

function connectSSE(stream) {
  if (_es) _es.close();
  const status = document.getElementById("gauge-status");
  if (status) { status.textContent = "Conectando…"; status.style.color = "var(--accent-violet)"; }
  _es = new EventSource("/stream/live");

  _es.onopen = () => {
    if (status) { status.textContent = "● Conectado"; status.style.color = "var(--accent-green)"; }
  };
  _es.onmessage = (ev) => {
    let msg;
    try { msg = JSON.parse(ev.data); } catch { return; }
    if (msg.type === "news_item") {
      if (stream.querySelector("[data-stream-empty]")) stream.innerHTML = "";
      prependNews(stream, msg.data, true);
    } else if (msg.type === "stats_update") {
      updateGauges(msg.data);
    }
  };
  _es.onerror = () => {
    if (status) { status.textContent = "Reconectando…"; status.style.color = "var(--accent-yellow)"; }
  };
}

async function setLiveState(action) {
  const response = await fetch("/api/live/toggle", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action }),
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}

function updateGauges(stats) {
  const total = stats.total || 1;
  const posPct = Math.round((stats.positive / total) * 100);
  const negPct = Math.round((stats.negative / total) * 100);
  setText("gauge-sentiment", posPct + "%");
  setText("gauge-news", stats.total || 0);
  setText("gauge-risk", negPct + "%");
  setWidth("gauge-sentiment-bar", posPct);
  setWidth("gauge-risk-bar", negPct);
}

// ---- Coleta RSS manual -----------------------------------------------------
window.MODULE_INIT.feed = function () {
  renderPortalChips("feed-portals", "feed");
  const btn = document.getElementById("feed-fetch");
  if (!btn) return;

  btn.addEventListener("click", async () => {
    const out = document.getElementById("feed-results");
    const count = document.getElementById("feed-count");
    const defaultLabel = btn.textContent;
    btn.disabled = true;
    btn.textContent = "Coletando…";
    out.innerHTML = `<div class="news-item"><div class="loading">Buscando notícias nos portais…</div></div>`;
    try {
      const resp = await fetch("/api/feed/fetch", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
      });
      const d = await resp.json();
      out.innerHTML = "";
      if (!d.news || !d.news.length) {
        out.innerHTML = `<div class="news-item"><div class="muted">Nenhuma notícia retornada (feeds podem estar indisponíveis).</div></div>`;
      } else {
        d.news.forEach((n) => prependNews(out, n, false));
      }
      if (count) count.textContent = `${d.count || 0} notícias`;
    } catch (e) {
      out.innerHTML = `<div class="news-item"><div class="error">Erro: ${e}</div></div>`;
    } finally {
      btn.disabled = false;
      btn.textContent = defaultLabel;
    }
  });
};

// ---- Helpers compartilhados ------------------------------------------------
function prependNews(container, n, prepend) {
  const cls = { positive: "pos", neutral: "neu", negative: "neg" }[n.sentiment] || "neu";
  const conf = Math.round((n.confidence || 0) * 100);
  const ents = (n.entities || []).map((e) => `<span class="entity-tag">${esc(e)}</span>`).join(" ");
  const el = document.createElement("div");
  el.className = "news-item";
  el.innerHTML = `
    <span class="sentiment-badge ${cls}">${n.sentiment.slice(0, 3).toUpperCase()} ${conf}%</span>
    <div class="news-text">
      <div class="news-headline">${esc(n.title)}</div>
      <div class="news-meta">
        <span class="news-source">${esc(n.portal)}</span>
        <div class="news-entities">${ents}</div>
      </div>
    </div>`;
  if (prepend && container.firstChild) container.insertBefore(el, container.firstChild);
  else container.appendChild(el);
}

function renderPortalChips(elId, mod) {
  const box = document.getElementById(elId);
  if (!box) return;
  fetch("/api/config").then((r) => r.json()).then((cfg) => {
    box.innerHTML = "";
    (cfg.all_portals || []).forEach((p) => {
      const on = cfg.active_portals.includes(p);
      const chip = document.createElement("span");
      chip.className = "portal-chip" + (on ? "" : " off");
      chip.textContent = p + (on ? " ✓" : "");
      chip.addEventListener("click", async () => {
        await fetch("/api/config", {
          method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ toggle_portal: p }),
        });
        renderPortalChips(elId, mod);
      });
      box.appendChild(chip);
    });
  });
}

function setText(id, v) { const e = document.getElementById(id); if (e) e.textContent = v; }
function setWidth(id, pct) { const e = document.getElementById(id); if (e) e.style.width = pct + "%"; }
function esc(s) {
  return String(s).replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])
  );
}
