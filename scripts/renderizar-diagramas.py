"""Renderiza los 52 diagramas a SVG y los deja listos para incrustar.

Dos decisiones que importan:

1. Se INCRUSTAN, no se referencian con <img>. Un SVG incrustado deja su texto en
   el HTML, así que las etiquetas de los diagramas pasan a ser contenido que un
   rastreador y un modelo pueden leer. Con <img> seguirían siendo invisibles, que
   es el problema que estamos arreglando.

2. Los colores fijos que emite mermaid se cambian por var(--dg-*, #fallback).
   Así el diagrama sigue el tema de la documentación, y si alguna vez se abre
   suelto el fallback reproduce la paleta. Es la misma técnica que usamos en el
   deck: nunca la mitad de un par color/fondo.

El mismo motor y el mismo tema para los 52 es lo que hace que las versiones en
español y en inglés queden idénticas por construcción, sin compararlas a ojo.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path('.')
SALIDA = RAIZ / 'src' / 'assets' / 'diagramas'
SALIDA.mkdir(parents=True, exist_ok=True)

# Centinela → token. El orden importa: primero los más largos para no romper
# coincidencias parciales.
TOKENS = [
    ('#0f172a', '--dg-text'),
    ('#334155', '--dg-muted'),
    ('#556577', '--dg-line'),
    ('#0369a1', '--dg-border'),
    ('#dbe7eb', '--dg-hairline'),
    ('#eef7f9', '--dg-surface-2'),
    ('#f3fafb', '--dg-surface'),
    ('#ffffff', '--dg-fill'),
]


def tokenizar(svg: str) -> tuple[str, int]:
    n = 0
    for hexa, token in TOKENS:
        for forma in (hexa, hexa.upper()):
            n += svg.count(forma)
            svg = svg.replace(forma, f'var({token}, {hexa})')
    # mermaid deja un id aleatorio por render; se fija para que el diff sea estable
    svg = re.sub(r'\bmy-svg\b', 'dg', svg)
    # sin ancho fijo: que lo gobierne el contenedor
    svg = re.sub(r'\s(width|height)="[\d.]+(px)?"', '', svg, count=2)
    return svg, n


def main() -> int:
    manifiesto = json.loads(Path('scripts/diagramas.json').read_text(encoding='utf8'))
    hechos, fallidos, cambios = 0, [], 0
    for d in manifiesto:
        destino = SALIDA / f"{d['id']}.svg"
        if destino.exists():
            hechos += 1
            continue
        tmp_in = Path('/tmp') / f"dg-{d['id']}.mmd"
        tmp_out = Path('/tmp') / f"dg-{d['id']}.svg"
        tmp_in.write_text(d['codigo'] + '\n', encoding='utf8')
        r = subprocess.run(
            [
                'node_modules/.bin/mmdc',
                '-i', str(tmp_in),
                '-o', str(tmp_out),
                '-c', 'scripts/render/mermaid.json',
                '-p', 'scripts/render/puppeteer.json',
                '-b', 'transparent',
            ],
            capture_output=True,
            text=True,
        )
        if r.returncode != 0 or not tmp_out.exists():
            fallidos.append((d['id'], d['archivo'], (r.stderr or r.stdout)[-160:]))
            continue
        svg, n = tokenizar(tmp_out.read_text(encoding='utf8'))
        destino.write_text(svg, encoding='utf8')
        cambios += n
        hechos += 1
        print(f"  ✓ {d['id']}  {d['tipo']:16} {Path(d['archivo']).parent.name}/{Path(d['archivo']).stem}")

    print(f'\n  renderizados: {hechos} de {len(manifiesto)}')
    print(f'  colores llevados a token: {cambios}')
    if fallidos:
        print(f'  ⚠ fallaron {len(fallidos)}:')
        for i, a, e in fallidos[:5]:
            print(f'    {i} {a}: {e}')
    return 1 if fallidos else 0


if __name__ == '__main__':
    sys.exit(main())
