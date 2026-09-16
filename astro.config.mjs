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
      /* La marca del encabezado la rinde SiteTitle con los MISMOS archivos del
         sitio: el cuervo y la marca de palabra, no un asset propio. Antes iba solo
         la marca de palabra en cian, asi que el simbolo de Moonin no aparecia. */
      favicon: "/favicon.png",
      locales: {
        root: { label: "English", lang: "en" },
        es: { label: "Español", lang: "es" },
      },
      /* Geist, con los mismos preconnect y la misma hoja que moonin.app: si la
         documentacion carga otra fuente, el cambio de soporte se nota al saltar. */
      head: [
        /* El icono de iOS, tambien el del sitio. */
        { tag: "link", attrs: { rel: "apple-touch-icon", sizes: "180x180", href: "/apple-touch-icon.png" } },
        /* Deteccion de idioma. Solo redirige desde la RAIZ y solo la primera vez:
           las URLs profundas quedan intactas porque Google recomienda no redirigir
           por idioma detectado, y la indexabilidad es justo lo que acabamos de
           arreglar. El sitemap ya declara los 120 alternates hreflang, que es la
           senal correcta para un rastreador. ?nolang lo desactiva.

           Tambien recuerda la eleccion explicita del selector de idioma, para que
           la deteccion no vuelva a pelear con lo que el usuario eligio. */
        {
          tag: "script",
          content: `(function(){try{
  var K='moonin-docs-lang', p=location.pathname;
  var raiz = (p==='/' || p==='/index.html');
  var guardado = localStorage.getItem(K);
  if (raiz && !guardado && location.search.indexOf('nolang')<0) {
    var tags = (navigator.languages && navigator.languages.length)
      ? navigator.languages : [navigator.language || 'en'];
    for (var i=0;i<tags.length;i++) {
      var base = String(tags[i]).toLowerCase().split('-')[0];
      if (base==='es') { localStorage.setItem(K,'es'); location.replace('/es/'); return; }
      if (base==='en') { break; }
    }
    localStorage.setItem(K,'en');
  }
  document.addEventListener('change', function(e){
    var el = e.target;
    if (el && el.closest && el.closest('starlight-lang-select')) {
      try { localStorage.setItem(K, String(el.value||'').indexOf('es')>=0 ? 'es' : 'en'); } catch(_) {}
    }
  }, true);
}catch(e){}})();`,
        },
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
      /* Los dos conmutadores se reemplazan por los botones del sitio: un cuadrado
         de 38px con sol o luna, y una pastilla con el idioma destino. Los
         desplegables de Starlight no se parecian a nada del resto. */
      components: {
        SiteTitle: "./src/components/SiteTitle.astro",
        ThemeSelect: "./src/components/ThemeSelect.astro",
        LanguageSelect: "./src/components/LanguageSelect.astro",
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
