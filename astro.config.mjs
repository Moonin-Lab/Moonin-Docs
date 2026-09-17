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
        /* Deteccion de idioma del navegador.
           
           Actua en CUALQUIER pagina y no solo en la raiz, porque un enlace compartido
           tambien merece abrirse en el idioma del lector.
           
           Y NO guarda nada cuando no redirige. La version anterior escribia 'en' en la
           primera visita aunque no hubiera redirigido, y con eso la deteccion quedaba
           apagada para siempre: bastaba una visita con el navegador en ingles para que
           un navegador en espanol nunca mas fuera atendido. Solo se guarda cuando el
           lector ELIGE con el boton de idioma.
           
           Sobre indexabilidad: los 60 alternates hreflang del sitemap y las etiquetas
           <link rel="alternate"> son la senal que Google usa para entender el par de
           idiomas, y siguen intactas. Este redirigir es de cliente, ocurre una vez,
           usa location.replace para no dejar rastro en el historial y se omite para los
           rastreadores conocidos. ?nolang lo desactiva. */
        {
          tag: "script",
          content: `(function(){try{
  var K='moonin-docs-lang';
  if (location.search.indexOf('nolang') >= 0) return;

  /* Nada de esto aplica a un rastreador: que vea la pagina que pidio. */
  var ua = (navigator.userAgent || '').toLowerCase();
  if (/bot|crawl|spider|slurp|bingpreview|headlesschrome|lighthouse|pagespeed/.test(ua)) return;

  var guardado = localStorage.getItem(K);
  var esEs = (function(){
    var t = (navigator.languages && navigator.languages.length)
      ? navigator.languages : [navigator.language || 'en'];
    for (var i = 0; i < t.length; i++) {
      var b = String(t[i]).toLowerCase().split('-')[0];
      if (b === 'es') return true;
      if (b === 'en') return false;
    }
    return false;
  })();

  var quiere = guardado === 'es' ? 'es' : guardado === 'en' ? 'en' : (esEs ? 'es' : 'en');
  var p = location.pathname;
  var estoyEn = (p === '/es' || p.indexOf('/es/') === 0) ? 'es' : 'en';

  if (quiere !== estoyEn) {
    var destino = quiere === 'es'
      ? '/es' + (p === '/' ? '/' : p)
      /* Doble backslash a proposito: esto vive dentro de un literal de plantilla,
         que consume \\/ y dejaria la expresion regular invalida. */
      : (p.replace(/^\\/es(?=\\/|$)/, '') || '/');
    if (destino !== p) { location.replace(destino + location.search + location.hash); return; }
  }

  /* La eleccion explicita del lector, que manda sobre la deteccion. */
  document.addEventListener('click', function(e){
    var a = e.target && e.target.closest && e.target.closest('[data-moonin-idioma]');
    if (a) { try { localStorage.setItem(K, a.getAttribute('lang') === 'es' ? 'es' : 'en'); } catch(_) {} }
  }, true);
}catch(e){}})();`,
        },        { tag: "link", attrs: { rel: "preconnect", href: "https://fonts.googleapis.com" } },
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
