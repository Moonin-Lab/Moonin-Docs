# Diagramas: de mermaid a SVG en el build

Los 52 diagramas de la documentación se incrustan como SVG durante el build. Antes
vivían sólo en el cliente: el HTML publicado llevaba el código fuente dentro de un
`<pre>` y ni un dibujo, así que ningún rastreador —ni ningún modelo al que se le
preguntara por la arquitectura— podía verlos.

Los `.md` no se tocan. La correspondencia va por el hash del código del diagrama.

## Cuándo hay que correr esto

Sólo si agregas o cambias un bloque ```mermaid. Si no lo corres, el diagrama nuevo
se dibuja en el navegador como antes: degrada, no rompe.

## Cómo

Hace falta un Chromium local. Se usa el que ya trae Playwright para no descargar
otro:

```sh
cat > scripts/render/puppeteer.json <<JSON
{ "executablePath": "RUTA/A/Chromium", "args": ["--no-sandbox"] }
JSON

npm i --no-save @mermaid-js/mermaid-cli
python3 scripts/extraer-diagramas.py      # lee los .md → scripts/diagramas.json
python3 scripts/renderizar-diagramas.py   # → src/assets/diagramas/*.svg
python3 scripts/ajustar-tamano-diagramas.py
```

El tercer paso importa: mermaid emite `width="100%"` y un `max-width`, y con eso
un flowchart horizontal de 2596px se encoge al ancho de la columna y su texto baja
a 4px. Medido sobre los 52, eso dejaba 31 ilegibles. El ajuste los devuelve a su
tamaño real y la figura desplaza cuando no cabe.

## Por qué se versionan los SVG

Para que GitHub Actions no necesite un navegador. El despliegue es el que ya
existía: push a `main`, Pages. Renderizar en el build habría obligado a instalar
Chromium en CI, y eso es cambiar la forma de desplegar.

## El tema

`scripts/render/mermaid.json` tiene los colores del build y
`src/scripts/mermaid-client.ts` los repite para el respaldo del navegador. Si
cambias uno, cambia el otro: si no, un diagrama dibujado en el cliente se verá
distinto de los otros cincuenta y dos.

Los colores fijos que emite mermaid se convierten en `var(--dg-*, #fallback)`, así
que los diagramas siguen el tema de la documentación y, abiertos suelos, el
fallback reproduce la paleta.
