"""Deja cada SVG en su tamaño natural, tomado de su propio viewBox.

Por qué no `width: 100%`: medido sobre los 52, forzarlos al ancho de la columna
—652px— deja a 31 de 47 con el texto por debajo de 9px, algunos en 4,3px, porque
son flowcharts horizontales de hasta 2596px de ancho. Y a los verticales les pasa
lo contrario: un diagrama de 154×631 se estiraría a 2667px de alto con texto de
59px.

La regla correcta para un diagrama es no reescalar su texto: se dibuja a su
tamaño y, si no cabe, la figura desplaza. Eso es lo que hace `.dg { overflow-x:
auto }` en portal.css.

mermaid emite `width="100%"` y un `max-width` en el style por su opción
useMaxWidth; las dos cosas fuerzan el encogido, así que se reemplazan por las
medidas reales del viewBox.
"""
import re
from pathlib import Path

DIR = Path('src/assets/diagramas')

ajustados, sin_viewbox = 0, []
for f in sorted(DIR.glob('*.svg')):
    s = f.read_text(encoding='utf8')
    m = re.search(r'<svg\b[^>]*>', s)
    if not m:
        sin_viewbox.append((f.name, 'sin etiqueta svg'))
        continue
    raiz = m.group(0)
    vb = re.search(r'viewBox="\s*([\d.-]+)\s+([\d.-]+)\s+([\d.]+)\s+([\d.]+)\s*"', raiz)
    if not vb:
        sin_viewbox.append((f.name, 'sin viewBox'))
        continue
    ancho, alto = round(float(vb.group(3))), round(float(vb.group(4)))

    nueva = raiz
    # width/height reales, no porcentaje
    nueva = re.sub(r'\swidth="[^"]*"', '', nueva)
    nueva = re.sub(r'\sheight="[^"]*"', '', nueva)
    nueva = nueva.replace('<svg', f'<svg width="{ancho}" height="{alto}"', 1)
    # fuera el max-width del style, que es lo que reintroduce el encogido
    def limpia_style(mm):
        css = re.sub(r'max-width\s*:[^;"]*;?\s*', '', mm.group(1))
        return f'style="{css.strip()}"' if css.strip() else ''
    nueva = re.sub(r'style="([^"]*)"', limpia_style, nueva)

    if nueva != raiz:
        f.write_text(s.replace(raiz, nueva, 1), encoding='utf8')
        ajustados += 1

print(f'  ajustados: {ajustados} de {len(list(DIR.glob("*.svg")))}')
if sin_viewbox:
    print(f'  ⚠ sin viewBox utilizable: {len(sin_viewbox)}')
    for n, r in sin_viewbox[:6]:
        print(f'    {n}: {r}')
