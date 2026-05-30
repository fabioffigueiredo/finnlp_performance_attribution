// =============================================================================
// FinNLP — app.js
// Navegação SPA-like: clica no sidebar → fetch do fragmento → injeta em #content.
// Mantém o sidebar persistente e o estado do SSE vivo entre módulos.
// =============================================================================

const content = document.getElementById("content");

async function loadModule(name, push = true) {
  document.querySelectorAll(".nav-item").forEach((el) =>
    el.classList.toggle("active", el.dataset.module === name)
  );
  try {
    const resp = await fetch(`/m/${name}`);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    content.innerHTML = await resp.text();
    if (push) history.pushState({ module: name }, "", `#${name}`);
    // Inicializador específico do módulo, se registrado
    if (window.MODULE_INIT && window.MODULE_INIT[name]) {
      window.MODULE_INIT[name]();
    }
  } catch (e) {
    content.innerHTML = `<div class="content-area"><div class="error">Erro ao carregar o módulo "${name}": ${e}</div></div>`;
  }
}

document.querySelectorAll(".nav-item").forEach((el) =>
  el.addEventListener("click", () => loadModule(el.dataset.module))
);

window.addEventListener("popstate", (e) => {
  const m = (e.state && e.state.module) || document.body.dataset.initial || "live";
  loadModule(m, false);
});

window.MODULE_INIT = window.MODULE_INIT || {};

// Carga inicial (módulo definido por data-initial, default = live)
const initial = document.body.dataset.initial || "live";
const fromHash = window.location.hash.replace("#", "");
loadModule(fromHash || initial, false);
