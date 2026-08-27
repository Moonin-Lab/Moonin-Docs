import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";

export default defineConfig({
  site: "https://docs.moonin.app",
  integrations: [
    starlight({
      title: "Moonin Documentation",
      logo: {
        src: "./src/assets/moonin-wordmark-cyan.svg",
        replacesTitle: true,
      },
      customCss: ["./src/styles/portal.css"],
      head: [
        {
          tag: "script",
          attrs: { type: "module" },
          content: `
            import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";

            let diagramIndex = 0;
            async function renderMermaid() {
              const blocks = document.querySelectorAll("pre > code.language-mermaid:not([data-moonin-rendered])");
              if (!blocks.length) return;
              mermaid.initialize({
                startOnLoad: false,
                theme: "base",
                securityLevel: "loose",
                themeVariables: {
                  primaryColor: "#e0f2fe",
                  primaryTextColor: "#0f172a",
                  primaryBorderColor: "#0ea5e9",
                  lineColor: "#0284c7",
                  secondaryColor: "#f0f9ff",
                  tertiaryColor: "#ffffff",
                  clusterBkg: "#f8fafc",
                  clusterBorder: "#cbd5e1",
                  fontFamily: "Inter, system-ui, sans-serif"
                }
              });
              await Promise.all([...blocks].map(async (code) => {
                code.dataset.mooninRendered = "true";
                const pre = code.parentElement;
                const target = document.createElement("div");
                target.className = "moonin-mermaid";
                const id = "moonin-mermaid-" + diagramIndex++;
                try {
                  const { svg } = await mermaid.render(id, code.textContent || "");
                  target.innerHTML = svg;
                  pre.replaceWith(target);
                } catch (error) {
                  console.error("Unable to render Mermaid diagram", error);
                  code.removeAttribute("data-moonin-rendered");
                }
              }));
            }
            document.addEventListener("astro:page-load", () => void renderMermaid());
          `,
        },
      ],
      sidebar: [
        { label: "Start Here", collapsed: true, items: [{ autogenerate: { directory: "getting-started" } }] },
        { label: "Agent", collapsed: true, items: [{ autogenerate: { directory: "agent" } }] },
        { label: "Deployments & Images", collapsed: true, items: [{ autogenerate: { directory: "deployments" } }] },
        { label: "Clusters & Nodes", collapsed: true, items: [{ autogenerate: { directory: "clusters" } }] },
        { label: "Workloads & Services", collapsed: true, items: [{ autogenerate: { directory: "workloads" } }] },
        { label: "Revisions", collapsed: true, items: [{ autogenerate: { directory: "revisions" } }] },
        { label: "Errors & Incidents", collapsed: true, items: [{ autogenerate: { directory: "incidents" } }] },
        { label: "Root Cause Analysis", collapsed: true, items: [{ autogenerate: { directory: "rca" } }] },
        { label: "Notifications", collapsed: true, items: [{ autogenerate: { directory: "notifications" } }] },
        { label: "Policies & Governance", collapsed: true, items: [{ autogenerate: { directory: "policies" } }] },
        { label: "Integrations", collapsed: true, items: [{ autogenerate: { directory: "integrations" } }] },
        { label: "Administration", collapsed: true, items: [{ autogenerate: { directory: "administration" } }] },
        { label: "FAQ", collapsed: true, items: [{ autogenerate: { directory: "faq" } }] },
        { label: "Glossary", slug: "glossary" },
        {
          label: "Español",
          collapsed: true,
          items: [
            { label: "Inicio", slug: "es" },
            { label: "Empezar aquí", collapsed: true, items: [{ autogenerate: { directory: "es/getting-started" } }] },
            { label: "Agente", collapsed: true, items: [{ autogenerate: { directory: "es/agent" } }] },
            { label: "Deployments e imágenes", collapsed: true, items: [{ autogenerate: { directory: "es/deployments" } }] },
            { label: "Clusters y nodos", collapsed: true, items: [{ autogenerate: { directory: "es/clusters" } }] },
            { label: "Workloads y servicios", collapsed: true, items: [{ autogenerate: { directory: "es/workloads" } }] },
            { label: "Revisiones", collapsed: true, items: [{ autogenerate: { directory: "es/revisions" } }] },
            { label: "Errores e incidentes", collapsed: true, items: [{ autogenerate: { directory: "es/incidents" } }] },
            { label: "Análisis de causa raíz", collapsed: true, items: [{ autogenerate: { directory: "es/rca" } }] },
            { label: "Notificaciones", collapsed: true, items: [{ autogenerate: { directory: "es/notifications" } }] },
            { label: "Políticas", collapsed: true, items: [{ autogenerate: { directory: "es/policies" } }] },
            { label: "Integraciones", collapsed: true, items: [{ autogenerate: { directory: "es/integrations" } }] },
            { label: "Administración", collapsed: true, items: [{ autogenerate: { directory: "es/administration" } }] },
            { label: "FAQ", collapsed: true, items: [{ autogenerate: { directory: "es/faq" } }] },
            { label: "Glosario", slug: "es/glossary" },
          ],
        },
      ],
    }),
  ],
});
