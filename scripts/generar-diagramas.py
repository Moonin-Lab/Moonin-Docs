"""Genera los 52 SVG eligiendo trazador según la forma de cada diagrama.

Tres caminos, porque tres formas distintas piden dibujos distintos:

  cadena lineal (40)   → trazador propio: riel vertical con pasos numerados
  con ramificación (7) → d2 con motor elk
  de secuencia (5)     → d2 con shape sequence_diagram

Se dejó de usar el trazador de mermaid porque su nodo es siempre un <rect> con una
etiqueta centrada: el techo estético estaba ahí y no en el CSS. Como efecto
secundario desaparece el desborde, porque la dirección LR que declara el markdown ya
no gobierna nada: la secuencia sale vertical y cabe en la columna.

Los colores se llevan a var(--dg-*, #fallback) para que los diagramas sigan el tema
de la documentación y, abiertos sueltos, el fallback reproduzca la paleta.
"""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import a_d2
import trazador

SALIDA = Path('src/assets/diagramas')

# Centinela → token. Los más largos primero para no romper coincidencias parciales.
TOKENS = [
    ('#0f172a', '--dg-text'),
    ('#475569', '--dg-muted'),
    ('#64748b', '--dg-faint'),
    ('#556577', '--dg-line'),
    ('#0a7ab8', '--dg-accent-hi'),
    ('#0369a1', '--dg-border'),
    ('#0b3a56', '--dg-accent-dk'),
    ('#8fc3d8', '--dg-rail-mid'),
    ('#cfe0e6', '--dg-rail'),
    ('#dbe7eb', '--dg-hairline'),
    ('#e9f6fa', '--dg-wash'),
    ('#eef7f9', '--dg-surface-2'),
    ('#f3fafb', '--dg-surface'),
    ('#ffffff', '--dg-fill'),
]


def tokenizar(svg: str) -> tuple[str, int]:
    n = 0
    for hexa, token in TOKENS:
        for forma in (hexa, hexa.upper()):
            c = svg.count(forma)
            if c:
                n += c
                svg = svg.replace(forma, f'var({token}, {hexa})')
    return svg, n


def sin_prologo(svg: str) -> str:
    svg = re.sub(r'<\?xml[^>]*\?>\s*', '', svg)
    svg = re.sub(r'<!DOCTYPE[^>]*>\s*', '', svg, flags=re.I)
    i = svg.find('<svg')
    return svg[i:] if i >= 0 else svg


def medidas(svg: str):
    m = re.search(r'viewBox="\s*[\d.-]+\s+[\d.-]+\s+([\d.]+)\s+([\d.]+)', svg)
    if m:
        return round(float(m.group(1))), round(float(m.group(2)))
    m = re.search(r'<svg[^>]*?width="([\d.]+)"[^>]*?height="([\d.]+)"', svg)
    return (round(float(m.group(1))), round(float(m.group(2)))) if m else (0, 0)


def fijar_tamano(svg: str) -> str:
    """Ancho y alto reales del viewBox, sin max-width: el diagrama no se reescala."""
    w, h = medidas(svg)
    if not w:
        return svg
    m = re.search(r'<svg[^>]*>', svg)
    raiz = m.group(0)
    nueva = re.sub(r'\s(?:width|height)="[^"]*"', '', raiz)
    nueva = re.sub(r'style="([^"]*)"',
                   lambda q: (lambda c: f'style="{c}"' if c else '')(
                       re.sub(r'max-width\s*:[^;"]*;?\s*', '', q.group(1)).strip()),
                   nueva)
    nueva = nueva.replace('<svg', f'<svg width="{w}" height="{h}"', 1)
    return svg.replace(raiz, nueva, 1)


# ── conversión de un diagrama de secuencia de mermaid a d2 ───────────────────
def secuencia_a_d2(codigo: str) -> str:
    partes, mensajes = {}, []
    for linea in codigo.splitlines():
        m = re.match(r'\s*participant\s+(\w+)\s+as\s+(.+?)\s*$', linea)
        if m:
            partes[m.group(1)] = m.group(2).strip()
            continue
        m = re.match(r'\s*(\w+)\s*(-{1,2}>>?|-{2}>>)\s*(\w+)\s*:\s*(.+?)\s*$', linea)
        if m:
            a, flecha, b, txt = m.group(1), m.group(2), m.group(3), m.group(4)
            mensajes.append((a, b, txt.strip(), flecha.startswith('--')))
    if not mensajes:
        return ''
    # La etiqueta vacía es necesaria: con nombre, d2 lo imprime como título
    # encima del diagrama, y "escena" no significa nada para el lector.
    L = ['vars: { d2-config: { layout-engine: elk } }', 'escena: "" {',
         '  shape: sequence_diagram']
    for k, v in partes.items():
        L.append(f'  {k}: "{v}"')
    for a, b, txt, punteada in mensajes:
        t = txt.replace('"', "'")
        if punteada:
            L.append(f'  {a} -> {b}: "{t}" {{ style.stroke-dash: 3 }}')
        else:
            L.append(f'  {a} -> {b}: "{t}"')
    P = a_d2.P
    L += [f'  *.style.fill: "{P["fill"]}"',
          f'  *.style.stroke: "{P["hairline"]}"',
          f'  *.style.font-color: "{P["text"]}"',
          f'  *.style.border-radius: 8',
          f'  (* -> *)[*].style.stroke: "{P["line"]}"',
          f'  (* -> *)[*].style.font-color: "{P["muted"]}"',
          f'  (* -> *)[*].style.font-size: 13',
          f'  *.style.font-size: 14',
          '}']
    return '\n'.join(L)


def main() -> int:
    man = json.loads(Path('scripts/diagramas.json').read_text(encoding='utf8'))
    SALIDA.mkdir(parents=True, exist_ok=True)
    for f in SALIDA.glob('*.svg'):
        f.unlink()

    cuenta = {'secuencia_propia': 0, 'grafo_d2': 0, 'secuencia_d2': 0}
    fallidos, anchos, colores = [], [], 0

    for d in man:
        # el hash debe seguir siendo el del código, para que el plugin lo encuentre
        ident = hashlib.sha1(d['codigo'].rstrip().encode('utf8')).hexdigest()[:12]
        assert ident == d['id'], f"hash cambió: {ident} != {d['id']}"
        destino = SALIDA / f'{ident}.svg'
        svg = None

        if d['tipo'] == 'sequenceDiagram':
            fuente = secuencia_a_d2(d['codigo'])
            if fuente and a_d2.dibujar(fuente, '/tmp/g.svg', pad=10):
                svg = Path('/tmp/g.svg').read_text(encoding='utf8')
                cuenta['secuencia_d2'] += 1
        else:
            etq, aristas = trazador.leer_grafo(d['codigo'])
            if aristas and trazador.es_cadena(aristas):
                svg = trazador.trazar_secuencia(etq, aristas)
                if svg:
                    cuenta['secuencia_propia'] += 1
            if svg is None and aristas:
                fuente = a_d2.a_d2(etq, aristas, direccion='down', motor='elk')
                if a_d2.dibujar(fuente, '/tmp/g.svg', pad=12):
                    svg = Path('/tmp/g.svg').read_text(encoding='utf8')
                    cuenta['grafo_d2'] += 1

        if not svg:
            fallidos.append((ident, d['archivo'], d['tipo']))
            continue

        svg = fijar_tamano(sin_prologo(svg))
        svg, n = tokenizar(svg)
        colores += n
        w, h = medidas(svg)
        anchos.append((w, h, d['archivo']))
        destino.write_text(svg, encoding='utf8')

    print(f'  por trazador: {cuenta}')
    print(f'  colores llevados a token: {colores}')
    print(f'  archivos: {len(list(SALIDA.glob("*.svg")))} de {len(man)}')
    if anchos:
        desbordan = [a for a in anchos if a[0] > 652]
        print(f'  ancho máximo: {max(a[0] for a in anchos)}px · '
              f'caben en la columna: {len(anchos)-len(desbordan)} de {len(anchos)}')
        for w, h, a in sorted(desbordan, reverse=True)[:5]:
            print(f'    desborda {w-652:4}px  {w}×{h}  {a.split("docs/")[-1]}')
    if fallidos:
        print(f'  ⚠ fallaron {len(fallidos)}:')
        for i, a, t in fallidos[:6]:
            print(f'    {i} {t} {a.split("docs/")[-1]}')
    return 1 if fallidos else 0


if __name__ == '__main__':
    sys.exit(main())
