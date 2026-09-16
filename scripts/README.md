# Diagramas: un trazador por forma de grafo

Los 52 diagramas se incrustan como SVG durante el build. Antes vivían sólo en el
cliente: el HTML publicado llevaba el código mermaid dentro de un `<pre>` y ni un
dibujo, así que ningún rastreador —ni ningún modelo al que se le preguntara por la
arquitectura— podía verlos.

Los `.md` no se tocan. La correspondencia va por el hash del código del diagrama.

## Por qué no se usa el trazador de mermaid

Su nodo es siempre un `<rect>` con una etiqueta centrada. Cambiarle relleno, borde y
peso tipográfico lo deja igual de inexpresivo: el techo estaba en el trazador.

Y al medir el contenido apareció lo que decidió el diseño: los 302 nodos son todos
rectángulos, sin un `classDef`, y **40 de los 47 flowcharts son cadenas lineales
puras**, sin una sola ramificación. Una secuencia no se dibuja con cajas y flechas;
se dibuja como secuencia.

## Los tres caminos

| forma | cuántos | trazador |
|---|---|---|
| cadena lineal | 38 | `trazador.py`, SVG propio: riel vertical con pasos numerados |
| con ramificación | 9 | `a_d2.py` → d2 con motor `elk` |
| de secuencia | 5 | d2 con `shape: sequence_diagram` |

`generar-diagramas.py` elige el camino leyendo la forma del grafo y escribe
`src/assets/diagramas/<hash12>.svg`.

La jerarquía se **deriva** del grafo, no se inventa: quien no recibe flechas es una
entrada, quien no emite es un resultado, quien concentra cuatro o más conexiones es
un eje. Es la única jerarquía que el contenido declara de verdad.

De los tres motores de d2, `elk` es el bueno: `tala` desparrama los nodos y
`--sketch` lee informal, que no es el registro de una documentación de
infraestructura.

## Cuándo hay que correr esto

Sólo si agregas o cambias un bloque ```mermaid. Si no lo corres, el diagrama nuevo
se dibuja en el navegador como antes: degrada, no rompe.

```sh
brew install d2
python3 scripts/extraer-diagramas.py    # lee los .md → scripts/diagramas.json
python3 scripts/generar-diagramas.py    # → src/assets/diagramas/*.svg
```

Ya no hace falta un Chromium: d2 es un binario y el trazador propio es Python.

## Por qué se versionan los SVG

Para que GitHub Actions no necesite nada. El despliegue es el que ya existía: push a
`main`, Pages.

## El tema

Los colores se llevan a `var(--dg-*, #fallback)`: los diagramas siguen el tema de la
documentación y, abiertos sueltos, el fallback reproduce la paleta. **Los doce tokens
deben existir en `src/styles/portal.css` con el mismo valor que su fallback** — si no
coinciden, el diagrama se ve distinto dentro y fuera del sitio.
