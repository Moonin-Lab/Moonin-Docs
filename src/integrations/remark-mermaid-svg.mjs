import { createHash } from "node:crypto";
import { readFileSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

/**
 * Reemplaza cada bloque ```mermaid por su SVG pre-renderizado.
 *
 * Por qué en el build y no en el navegador: la integración anterior sólo
 * inyectaba un script de cliente, así que el HTML publicado llevaba el código
 * fuente del diagrama dentro de un <pre> y ni un solo SVG. Los 52 diagramas de
 * la documentación eran invisibles para un rastreador y para cualquier modelo al
 * que le preguntaran por la arquitectura.
 *
 * El SVG se INCRUSTA, no se referencia con <img>: incrustado, sus etiquetas son
 * texto del documento y se pueden indexar; con <img> seguirían siendo píxeles.
 *
 * Los .md no se tocan. La correspondencia va por el hash del código del
 * diagrama, el mismo que calcula scripts/extraer-diagramas.py, de modo que las
 * versiones en español y en inglés —que tienen etiquetas distintas— obtienen
 * cada una su archivo, renderizado por el mismo motor y con el mismo tema. Ahí
 * está la garantía de que el diseño sea idéntico entre idiomas.
 *
 * Si un diagrama no tiene SVG —porque alguien agregó uno y no corrió el
 * renderizador— el bloque se deja intacto y el cliente lo dibuja como antes.
 * Degrada, no rompe.
 */

const AQUI = dirname(fileURLToPath(import.meta.url));
const DIR_SVG = join(AQUI, "..", "assets", "diagramas");

function idDe(codigo) {
  return createHash("sha1")
    .update(codigo.replace(/\s+$/, ""), "utf8")
    .digest("hex")
    .slice(0, 12);
}

export function remarkMermaidSvg() {
  return (arbol) => {
    const pendientes = [];

    const visitar = (nodo, indice, padre) => {
      if (nodo.type === "code" && nodo.lang === "mermaid") {
        pendientes.push({ nodo, indice, padre });
      }
      if (Array.isArray(nodo.children)) {
        nodo.children.forEach((hijo, i) => visitar(hijo, i, nodo));
      }
    };
    visitar(arbol, 0, null);

    /* De atrás hacia adelante: reemplazar en orden movería los índices de los
       hermanos que faltan por procesar. */
    for (const { nodo, indice, padre } of pendientes.reverse()) {
      const ruta = join(DIR_SVG, `${idDe(nodo.value)}.svg`);
      if (!existsSync(ruta)) continue;

      const svg = readFileSync(ruta, "utf8")
        .replace(/^<\?xml[^>]*\?>\s*/, "")
        .replace(/<!DOCTYPE[^>]*>\s*/i, "");

      /* role="img" con la primera línea del código como descripción: da un
         nombre accesible sin inventar texto que no esté en la fuente. */
      const tipo = nodo.value.trim().split("\n")[0].trim();
      padre.children[indice] = {
        type: "html",
        value:
          `<figure class="dg" role="img" aria-label="${tipo.replace(/"/g, "&quot;")}">` +
          svg +
          `</figure>`,
      };
    }
  };
}

export default remarkMermaidSvg;
