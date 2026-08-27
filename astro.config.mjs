import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";
import { mermaid } from "./src/integrations/mermaid";

export default defineConfig({
  site: "https://docs.moonin.app",
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
