/*
 * Deja /sitemap.xml como el LISTADO COMPLETO de las 60 URLs, no como otro índice.
 *
 * Starlight emite sitemap-index.xml, que apunta a sitemap-0.xml. Un índice no declara
 * páginas, así que Search Console lo muestra con «0 páginas descubiertas» hasta que
 * procesa el hijo, por separado y más tarde. Es correcto, pero parece un fallo.
 *
 * Con 60 URLs el índice no aporta nada: el límite por archivo son 50.000. Así que
 * /sitemap.xml pasa a ser el urlset entero y quien lo envíe ve las 60 de inmediato.
 * El índice y el hijo se conservan, porque robots.txt anuncia el índice y puede haber
 * herramientas que ya lo tengan registrado.
 */
import { copyFileSync, existsSync, readFileSync } from "node:fs";
import { join } from "node:path";

const dist = "dist";
const hijo = join(dist, "sitemap-0.xml");
const destino = join(dist, "sitemap.xml");

if (!existsSync(hijo)) {
  console.error(`sitemap-plano: no existe ${hijo}; ¿cambió el nombre que emite Starlight?`);
  process.exit(1);
}

copyFileSync(hijo, destino);

const contenido = readFileSync(destino, "utf8");
const urls = (contenido.match(/<loc>/g) || []).length;
const alternates = (contenido.match(/hreflang=/g) || []).length;
if (urls === 0) {
  console.error("sitemap-plano: el archivo copiado no declara ninguna URL");
  process.exit(1);
}
console.log(`sitemap-plano: /sitemap.xml con ${urls} URLs y ${alternates} alternates hreflang`);
