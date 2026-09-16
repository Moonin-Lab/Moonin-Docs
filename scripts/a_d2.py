"""Convierte el código mermaid a d2 y lo dibuja con un tema propio.

d2 tiene un techo estético bastante más alto que mermaid: radios, sombras reales,
modo bosquejo, y tres motores de trazado (dagre, elk, tala) con enrutado de aristas
mucho mejor. Lo que mermaid no permite —cambiar la forma del nodo según su papel,
sombras, degradados— aquí es una propiedad.

El papel de cada nodo se sigue derivando del grafo, no se inventa.
"""
import re
import subprocess
from pathlib import Path

P = {
    'text': '#0f172a', 'muted': '#475569', 'accent': '#0369a1',
    'accent_dk': '#0b3a56', 'wash': '#e9f6fa', 'hairline': '#dbe7eb',
    'surface': '#f8fcfd', 'fill': '#ffffff', 'line': '#556577',
}


def papeles(aristas, nodos):
    ent, sal = {}, {}
    for a, b, _ in aristas:
        sal[a] = sal.get(a, 0) + 1
        ent[b] = ent.get(b, 0) + 1
    r = {}
    for n in nodos:
        i, o = ent.get(n, 0), sal.get(n, 0)
        if i == 0 and o > 0:
            r[n] = 'entrada'
        elif o == 0 and i > 0:
            r[n] = 'resultado'
        elif i + o >= 4:
            r[n] = 'eje'
        else:
            r[n] = 'paso'
    return r


CLASES = f"""classes: {{
  entrada: {{
    style: {{
      fill: "{P['accent']}"
      stroke: "{P['accent']}"
      font-color: "{P['fill']}"
      bold: true
      border-radius: 10
      shadow: true
      stroke-width: 1
    }}
  }}
  eje: {{
    style: {{
      fill: "{P['fill']}"
      stroke: "{P['accent']}"
      font-color: "{P['text']}"
      bold: true
      border-radius: 10
      stroke-width: 2
      shadow: true
    }}
  }}
  paso: {{
    style: {{
      fill: "{P['fill']}"
      stroke: "{P['hairline']}"
      font-color: "{P['text']}"
      border-radius: 10
      stroke-width: 1
      shadow: true
    }}
  }}
  resultado: {{
    style: {{
      fill: "{P['wash']}"
      stroke: "{P['accent']}"
      font-color: "{P['accent_dk']}"
      bold: true
      border-radius: 10
      stroke-width: 1
      shadow: true
    }}
  }}
}}"""


def a_d2(etq, aristas, direccion='down', motor='elk') -> str:
    nodos = list(etq) or sorted({x for a, b, _ in aristas for x in (a, b)})
    rol = papeles(aristas, nodos)
    L = [f'vars: {{ d2-config: {{ layout-engine: {motor} }} }}',
         f'direction: {direccion}', '',
         CLASES, '']
    for n in nodos:
        texto = re.sub(r'<br\s*/?>', r'\\n', etq.get(n, n)).replace('"', "'")
        L.append(f'{n}: "{texto}" {{ class: {rol.get(n, "paso")} }}')
    L.append('')
    for a, b, et in aristas:
        if et:
            L.append(f'{a} -> {b}: "{et}"')
        else:
            L.append(f'{a} -> {b}')
    L.append('')
    L.append(f'''*.style.font-size: 14
(* -> *)[*].style.stroke: "{P['line']}"
(* -> *)[*].style.stroke-width: 2
(* -> *)[*].style.font-size: 12
(* -> *)[*].style.font-color: "{P['muted']}"''')
    return '\n'.join(L)


def dibujar(fuente_d2: str, salida: str, bosquejo=False, pad=14) -> bool:
    ent = Path('/tmp/conv.d2')
    ent.write_text(fuente_d2, encoding='utf8')
    cmd = ['d2', '--pad', str(pad), '--dark-theme', '-1']
    if bosquejo:
        cmd.append('--sketch')
    cmd += [str(ent), salida]
    r = subprocess.run(cmd, capture_output=True, text=True)
    ok = Path(salida).exists() and Path(salida).stat().st_size > 0
    if not ok:
        print(f'      d2 falló: {(r.stderr or r.stdout)[-200:]}')
    return ok
