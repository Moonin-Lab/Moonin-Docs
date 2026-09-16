import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";
import { mermaid } from "./src/integrations/mermaid";
import { remarkMermaidSvg } from "./src/integrations/remark-mermaid-svg.mjs";

export default defineConfig({
  site: "https://docs.moonin.app",
  /* Los diagramas se incrustan como SVG durante el build. Antes vivian solo en
     el cliente, asi que el HTML publicado llevaba el codigo fuente y ningun
     dibujo: 52 diagramas que un rastreador no podia ver. */
  markdown: { remarkPlugins: [remarkMermaidSvg] },
  integrations: [
    mermaid(),
    starlight({
      title: "Moonin Documentation",
      logo: {
        src: "./src/assets/moonin-wordmark-cyan.svg",
        replacesTitle: true,
      },
      locales: {
        root: { label: "English", lang: "en" },
        es: { label: "Español", lang: "es" },
      },
      /* Geist, con los mismos preconnect y la misma hoja que moonin.app: si la
         documentacion carga otra fuente, el cambio de soporte se nota al saltar. */
      head: [
        { tag: "link", attrs: { rel: "preconnect", href: "https://fonts.googleapis.com" } },
        { tag: "link", attrs: { rel: "preconnect", href: "https://fonts.gstatic.com", crossorigin: true } },
        {
          tag: "link",
          attrs: {
            rel: "stylesheet",
            href: "https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&family=Geist+Mono:wght@400;500&display=swap",
          },
        },
      ],
      customCss: ["./src/styles/portal.css"],
      sidebar: [
          {
            label: "Start Here",
            translations: { es: "Empezar aquí" },
            collapsed: true,
            items: [{ autogenerate: { directory: "getting-started" } }],
          },
          {
            label: "Agent",
            translations: { es: "Agente" },
            collapsed: true,
            items: [{ autogenerate: { directory: "agent" } }],
          },
          {
            label: "Deployments & Images",
            translations: { es: "Deployments e imágenes" },
            collapsed: true,
            items: [{ autogenerate: { directory: "deployments" } }],
          },
          {
            label: "Clusters & Nodes",
            translations: { es: "Clusters y nodos" },
            collapsed: true,
            items: [{ autogenerate: { directory: "clusters" } }],
          },
          {
            label: "Workloads & Services",
            translations: { es: "Workloads y servicios" },
            collapsed: true,
            items: [{ autogenerate: { directory: "workloads" } }],
          },
          {
            label: "Revisions",
            translations: { es: "Revisiones" },
            collapsed: true,
            items: [{ autogenerate: { directory: "revisions" } }],
          },
          {
            label: "Errors & Incidents",
            translations: { es: "Errores e incidentes" },
            collapsed: true,
            items: [{ autogenerate: { directory: "incidents" } }],
          },
          {
            label: "Root Cause Analysis",
            translations: { es: "Análisis de causa raíz" },
            collapsed: true,
            items: [{ autogenerate: { directory: "rca" } }],
          },
          {
            label: "Notifications",
            translations: { es: "Notificaciones" },
            collapsed: true,
            items: [{ autogenerate: { directory: "notifications" } }],
          },
          {
            label: "Policies & Governance",
            translations: { es: "Políticas" },
            collapsed: true,
            items: [{ autogenerate: { directory: "policies" } }],
          },
          {
            label: "Integrations",
            translations: { es: "Integraciones" },
            collapsed: true,
            items: [{ autogenerate: { directory: "integrations" } }],
          },
          {
            label: "Administration",
            translations: { es: "Administración" },
            collapsed: true,
            items: [{ autogenerate: { directory: "administration" } }],
          },
          {
            label: "FAQ",
            translations: { es: "FAQ" },
            collapsed: true,
            items: [{ autogenerate: { directory: "faq" } }],
          },
          { label: "Glossary", translations: { es: "Glosario" }, slug: "glossary" },
        ],
    }),
  ],
});
