/* Carga diferida: con los diagramas ya incrustados como SVG en el build, la
   mayoria de las paginas no tiene ningun bloque mermaid, y la libreria pesa
   cerca de 500 KB. Se importa solo si queda alguno por dibujar. */


function labelCopyButtons() {
  const es = document.documentElement.lang?.startsWith("es");
  for (const ec of document.querySelectorAll(".expressive-code")) {
    // Skip Mermaid blocks: they are rendered as diagrams, not code.
    if (ec.querySelector('pre[data-language="mermaid"]')) continue;
    if (ec.querySelector("[data-moonin-bar]")) continue;
    const lang = (ec.querySelector("pre")?.getAttribute("data-language") || "code").toUpperCase();
    const bar = document.createElement("div");
    bar.setAttribute("data-moonin-bar", "");
    bar.className = "moonin-codebar";
    const title = document.createElement("span");
    title.className = "moonin-codebar-title";
    title.textContent = lang;
    const copy = document.createElement("button");
    copy.type = "button";
    copy.className = "moonin-codebar-copy";
    copy.textContent = es ? "Copiar" : "Copy";
    copy.addEventListener("click", () => {
      const native = ec.querySelector(".copy button");
      if (native instanceof HTMLButtonElement) native.click();
      copy.textContent = es ? "¡Copiado!" : "Copied!";
      setTimeout(() => {
        copy.textContent = es ? "Copiar" : "Copy";
      }, 1600);
    });
    bar.append(title, copy);
    ec.prepend(bar);
  }
}

function apply() {
  labelCopyButtons();
}
document.addEventListener("astro:page-load", () => setTimeout(apply, 0));
document.addEventListener("DOMContentLoaded", apply);
setTimeout(apply, 120);
apply();

/* Respaldo, no camino principal. Los diagramas se incrustan como SVG durante el
   build, asi que en condiciones normales no queda ningun bloque que dibujar aqui.
   Esto cubre el caso de que alguien agregue un diagrama y no corra el
   renderizador: la pagina lo dibuja igual, en vez de mostrar codigo crudo.

   Los colores replican los del renderizador de build (scripts/render/mermaid.json)
   para que un diagrama dibujado por este respaldo no se vea distinto de los otros
   cincuenta y dos. Si se cambian alla, hay que cambiarlos aca. */
const configMermaid = {
  startOnLoad: false,
  theme: "base" as const,
  securityLevel: "loose" as const,
  htmlLabels: false,
  flowchart: { curve: "basis" as const, padding: 14, useMaxWidth: true, htmlLabels: false },
  sequence: { useMaxWidth: true, wrap: true },
  themeVariables: {
    fontFamily: "Geist, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif",
    fontSize: "14px",
    primaryColor: "#ffffff",
    primaryTextColor: "#0f172a",
    primaryBorderColor: "#0369a1",
    secondaryColor: "#f3fafb",
    secondaryBorderColor: "#dbe7eb",
    tertiaryColor: "#eef7f9",
    tertiaryBorderColor: "#dbe7eb",
    lineColor: "#556577",
    textColor: "#0f172a",
    mainBkg: "#ffffff",
    nodeBorder: "#0369a1",
    clusterBkg: "#f3fafb",
    clusterBorder: "#dbe7eb",
    actorBkg: "#ffffff",
    actorBorder: "#0369a1",
    actorTextColor: "#0f172a",
    signalColor: "#556577",
    signalTextColor: "#334155",
    labelBoxBkgColor: "#f3fafb",
    labelBoxBorderColor: "#dbe7eb",
    noteBkgColor: "#eef7f9",
    noteBorderColor: "#dbe7eb",
    noteTextColor: "#334155",
  },
};

let index = 0;

async function renderDiagrams() {
  const blocks = Array.from(
    document.querySelectorAll("pre[data-language='mermaid']:not([data-moonin-rendered])"),
  );
  /* La salida temprana es el punto de todo esto: sin ella se descargaban ~500 KB
     de mermaid en cada pagina de la documentacion para no dibujar nada. */
  if (blocks.length === 0) return;

  const { default: mermaid } = await import("mermaid");
  mermaid.initialize(configMermaid);

  for (const block of blocks) {
    (block as HTMLElement).dataset.mooninRendered = "true";
    const container = document.createElement("div");
    container.className = "moonin-mermaid";
    const id = "moonin-mermaid-" + index++;
    const lines = Array.from(block.querySelectorAll(".ec-line")).map(
      (line) => line.textContent || "",
    );
    const source = lines.length ? lines.join("\n") : block.textContent || "";
    try {
      const { svg } = await mermaid.render(id, source);
      container.innerHTML = svg;
      const host = block.closest(".expressive-code") || block;
      host.replaceWith(container);
    } catch (error) {
      console.error("Unable to render Mermaid diagram", error);
      block.removeAttribute("data-moonin-rendered");
    }
  }
}

document.addEventListener("astro:page-load", () => void renderDiagrams());
void renderDiagrams();
