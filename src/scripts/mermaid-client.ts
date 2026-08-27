import mermaid from "mermaid";

function forceCodeTheme() {
  document.documentElement.dataset.theme = "dark";
}

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
  forceCodeTheme();
  labelCopyButtons();
}
document.addEventListener("astro:page-load", () => setTimeout(apply, 0));
document.addEventListener("DOMContentLoaded", apply);
setTimeout(apply, 120);
apply();

mermaid.initialize({
  startOnLoad: false,
  theme: "base",
  securityLevel: "loose",
  themeVariables: {
    primaryColor: "#ffffff",
    primaryTextColor: "#0f172a",
    primaryBorderColor: "#0ea5e9",
    lineColor: "#0284c7",
    secondaryColor: "#e0f2fe",
    tertiaryColor: "#ffffff",
    clusterBkg: "#f1f9ff",
    clusterBorder: "#7dd3fc",
    noteBkgColor: "#fffbeb",
    noteTextColor: "#78350f",
    noteBorderColor: "#fcd34d",
    actorBkg: "#ffffff",
    actorBorder: "#0ea5e9",
    actorTextColor: "#0f172a",
    activationBkgColor: "#bae6fd",
    signalColor: "#0ea5e9",
    signalTextColor: "#f0f9ff",
    labelBoxBkgColor: "#ffffff",
    labelBoxBorderColor: "#bae6fd",
    fontFamily: "Inter, system-ui, sans-serif",
  },
});

let index = 0;

async function renderDiagrams() {
  const blocks = Array.from(
    document.querySelectorAll("pre[data-language='mermaid']:not([data-moonin-rendered])"),
  );
  for (const block of blocks) {
    block.dataset.mooninRendered = "true";
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