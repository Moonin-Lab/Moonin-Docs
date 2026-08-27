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
      sidebar: [
        { label: "Start Here", items: [{ autogenerate: { directory: "getting-started" } }] },
        { label: "Agent", items: [{ autogenerate: { directory: "agent" } }] },
        { label: "Deployments & Images", items: [{ autogenerate: { directory: "deployments" } }] },
        { label: "Clusters & Nodes", items: [{ autogenerate: { directory: "clusters" } }] },
        { label: "Workloads & Services", items: [{ autogenerate: { directory: "workloads" } }] },
        { label: "Revisions", items: [{ autogenerate: { directory: "revisions" } }] },
        { label: "Errors & Incidents", items: [{ autogenerate: { directory: "incidents" } }] },
        { label: "Root Cause Analysis", items: [{ autogenerate: { directory: "rca" } }] },
        { label: "Notifications", items: [{ autogenerate: { directory: "notifications" } }] },
        { label: "Policies & Governance", items: [{ autogenerate: { directory: "policies" } }] },
        { label: "Integrations", items: [{ autogenerate: { directory: "integrations" } }] },
        { label: "Administration", items: [{ autogenerate: { directory: "administration" } }] },
        { label: "FAQ", items: [{ autogenerate: { directory: "faq" } }] },
        { label: "Glossary", slug: "glossary" },
        {
          label: "Español",
          items: [
            { label: "Inicio", slug: "es" },
            { label: "Empezar aquí", items: [{ autogenerate: { directory: "es/getting-started" } }] },
            { label: "Agente", items: [{ autogenerate: { directory: "es/agent" } }] },
            { label: "Deployments e imágenes", items: [{ autogenerate: { directory: "es/deployments" } }] },
            { label: "Clusters y nodos", items: [{ autogenerate: { directory: "es/clusters" } }] },
            { label: "Workloads y servicios", items: [{ autogenerate: { directory: "es/workloads" } }] },
            { label: "Revisiones", items: [{ autogenerate: { directory: "es/revisions" } }] },
            { label: "Errores e incidentes", items: [{ autogenerate: { directory: "es/incidents" } }] },
            { label: "Análisis de causa raíz", items: [{ autogenerate: { directory: "es/rca" } }] },
            { label: "Notificaciones", items: [{ autogenerate: { directory: "es/notifications" } }] },
            { label: "Políticas", items: [{ autogenerate: { directory: "es/policies" } }] },
            { label: "Integraciones", items: [{ autogenerate: { directory: "es/integrations" } }] },
            { label: "Administración", items: [{ autogenerate: { directory: "es/administration" } }] },
            { label: "FAQ", items: [{ autogenerate: { directory: "es/faq" } }] },
            { label: "Glosario", slug: "es/glossary" },
          ],
        },
      ],
    }),
  ],
});
