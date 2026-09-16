"""Extrae los bloques mermaid de la documentación a un manifiesto.

No toca los .md: solo los lee. Cada diagrama se identifica por el hash de su
código, así que dos páginas con el mismo diagrama comparten un SVG y las
versiones en español —que llevan etiquetas traducidas— obtienen el suyo.
Renderizarlos todos con el mismo motor y el mismo tema es lo que garantiza que
el diseño sea idéntico entre idiomas, en vez de tener que compararlos a ojo.
"""
import hashlib
import json
import re
from pathlib import Path

RAIZ = Path('src/content/docs')
CERCA = re.compile(r'^([ \t]*)```mermaid[ \t]*\n(.*?)^\1```[ \t]*$', re.M | re.S)

manifiesto = []
for md in sorted(RAIZ.rglob('*.md')):
    texto = md.read_text(encoding='utf8')
    for n, m in enumerate(CERCA.finditer(texto)):
        codigo = m.group(2).rstrip()
        idioma = 'es' if md.relative_to(RAIZ).parts[0] == 'es' else 'en'
        manifiesto.append(
            {
                'id': hashlib.sha1(codigo.encode('utf8')).hexdigest()[:12],
                'archivo': str(md),
                'indice': n,
                'idioma': idioma,
                'tipo': codigo.split('\n')[0].split()[0] if codigo.strip() else '?',
                'lineas': len(codigo.split('\n')),
                'codigo': codigo,
            }
        )

Path('scripts/diagramas.json').write_text(
    json.dumps(manifiesto, ensure_ascii=False, indent=1), encoding='utf8'
)

unicos = {d['id'] for d in manifiesto}
por_idioma = {}
for d in manifiesto:
    por_idioma.setdefault(d['idioma'], set()).add(d['id'])

print(f'  diagramas encontrados: {len(manifiesto)}')
print(f'  únicos por contenido:  {len(unicos)}')
for k, v in sorted(por_idioma.items()):
    print(f'    {k}: {len(v)} únicos')
comp = por_idioma.get('es', set()) & por_idioma.get('en', set())
print(f'  compartidos entre idiomas (sin texto traducible): {len(comp)}')
tipos = {}
for d in manifiesto:
    tipos[d['tipo']] = tipos.get(d['tipo'], 0) + 1
print(f'  tipos: {tipos}')
print(f'  el más largo: {max(d["lineas"] for d in manifiesto)} líneas')
