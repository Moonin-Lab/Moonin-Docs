"""Trazador propio de diagramas. Dibuja el SVG en vez de pedírselo a mermaid.

Por qué dejar mermaid: un nodo de mermaid es siempre un <rect> con una etiqueta
centrada. Se le puede cambiar el relleno y el peso del tipo, pero sigue siendo una
caja; el techo estético no está en el CSS, está en el trazador.

Y sobre todo: 40 de los 47 flowcharts son CADENAS LINEALES puras, sin una sola
ramificación. Una secuencia no se dibuja con cajas y flechas, se dibuja como una
secuencia: un riel vertical con pasos numerados. Eso además hace desaparecer el
problema del ancho —una secuencia vertical mide 620 de ancho y cabe en la columna—
sin tocar una sola palabra del contenido.

Los identificadores de cada región son estables (`paso-3`, `riel`, `tarjeta-3`) para
poder afinar una zona sin redibujar todo.
"""
import html
import re

# ── paleta, la misma del sitio ────────────────────────────────────────────────
P = {
    'text': '#0f172a', 'muted': '#475569', 'faint': '#64748b',
    'accent': '#0369a1', 'accent_dk': '#0b3a56', 'accent_wash': '#e9f6fa',
    'hairline': '#dbe7eb', 'rail': '#cfe0e6', 'surface': '#f3fafb',  # el mismo tono del sitio
    'fill': '#ffffff',
}
# Comillas SIMPLES en el nombre con espacio: la cadena va dentro de un atributo
# SVG entre comillas dobles, y anidar dobles produce XML inválido.
FUENTE = ("Geist, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, "
          "Helvetica, Arial, sans-serif")

# anchos relativos por carácter a 1em, para partir líneas sin un navegador
_ESTRECHO = set('iljtfrI.,:;\'"|!()[]{}-')
_ANCHO = set('mwMW@')
_MAYUS = set('ABCDEFGHJKLNOPQRSTUVXYZ')


def _ancho(txt: str, tam: float) -> float:
    u = 0.0
    for c in txt:
        if c == ' ':
            u += 0.27
        elif c in _ESTRECHO:
            u += 0.32
        elif c in _ANCHO:
            u += 0.87
        elif c in _MAYUS:
            u += 0.64
        elif c.isdigit():
            u += 0.56
        else:
            u += 0.525
    return u * tam


def _partir(txt: str, tam: float, limite: float) -> list[str]:
    """Parte en líneas sin cortar palabras."""
    lineas, actual = [], ''
    for pal in txt.split():
        prueba = f'{actual} {pal}'.strip()
        if _ancho(prueba, tam) <= limite or not actual:
            actual = prueba
        else:
            lineas.append(actual)
            actual = pal
    if actual:
        lineas.append(actual)
    return lineas


def _e(s: str) -> str:
    return html.escape(s, quote=True)


# ── lectura del código mermaid ────────────────────────────────────────────────
def leer_grafo(codigo: str):
    """Devuelve (etiquetas, aristas) del código, sin depender de mermaid."""
    etq, aristas = {}, []
    for m in re.finditer(r'([A-Za-z0-9_]+)\s*\[([^\]]+)\]', codigo):
        etq[m.group(1)] = m.group(2).strip()
    for linea in codigo.splitlines():
        et = re.findall(r'\|([^|]*)\|', linea)
        limpia = re.sub(r'\|[^|]*\|', '\x00', linea)
        if not re.search(r'-{2,3}>|-\.->|={2,3}>', limpia):
            continue
        trozos = re.split(r'-{2,3}>|-\.->|={2,3}>', limpia)
        nodos = []
        for t in trozos:
            m = re.match(r'\s*\x00?\s*([A-Za-z0-9_]+)', t)
            if m:
                nodos.append(m.group(1))
        for i, (a, b) in enumerate(zip(nodos, nodos[1:])):
            aristas.append((a, b, et[i].strip() if i < len(et) else ''))
    return etq, aristas


def es_cadena(aristas) -> bool:
    """Cadena lineal pura: cada nodo emite y recibe a lo más una vez."""
    sal, ent = {}, {}
    for a, b, _ in aristas:
        sal[a] = sal.get(a, 0) + 1
        ent[b] = ent.get(b, 0) + 1
    return bool(aristas) and max(sal.values()) == 1 and max(ent.values()) == 1


def orden_cadena(aristas):
    sig = {a: b for a, b, _ in aristas}
    etiqueta = {(a, b): t for a, b, t in aristas}
    destinos = set(sig.values())
    inicio = next((a for a in sig if a not in destinos), None)
    if inicio is None:
        return [], {}
    orden, visto = [inicio], {inicio}
    while orden[-1] in sig and sig[orden[-1]] not in visto:
        orden.append(sig[orden[-1]])
        visto.add(orden[-1])
    return orden, etiqueta


# ── el trazador de secuencias ────────────────────────────────────────────────
def trazar_secuencia(etq, aristas, ancho=624):
    """Riel vertical con pasos numerados. Para las 40 cadenas lineales.

    El número no es decoración: el contenido ES una secuencia, así que numerarla
    informa. En un grafo con ramificación estaría de más y por eso no se usa allí.
    """
    orden, etiqueta_arista = orden_cadena(aristas)
    if not orden:
        return None

    # geometría
    RIEL_X, DISCO = 26, 27
    TAR_X = RIEL_X + DISCO / 2 + 26
    TAR_W = ancho - TAR_X - 14
    PAD_X, PAD_Y = 19, 16
    TAM, INTER = 14, 20.5
    HUECO = 15

    piezas, y = [], 16
    centros = []
    for i, n in enumerate(orden):
        crudo = etq.get(n, n)
        partes = re.split(r'<br\s*/?>', crudo)
        titulo = partes[0].strip()
        sub = partes[1].strip() if len(partes) > 1 else ''
        lineas = _partir(titulo, TAM, TAR_W - 2 * PAD_X)
        alto_txt = len(lineas) * INTER + (15 if sub else 0)
        alto = max(50, alto_txt + 2 * PAD_Y)
        ultimo = i == len(orden) - 1
        # La tarjeta abraza su texto en vez de estirarse al ancho completo: ocho
        # barras idénticas no tienen ritmo, ocho anchos distintos sí. El mínimo
        # evita que una etiqueta corta quede como una pastilla suelta.
        med = max([_ancho(l, TAM) for l in lineas] +
                  ([_ancho(sub, 11.5)] if sub else []))
        w_tar = min(TAR_W, max(228, med + 2 * PAD_X + 8))

        borde = P['accent'] if ultimo else P['hairline']
        relleno = 'url(#dgGradLlegada)' if ultimo else 'url(#dgGrad)'
        centros.append(y + alto / 2)

        piezas.append(f'<g id="paso-{i+1}">')
        piezas.append(
            f'<line x1="{RIEL_X + DISCO/2}" y1="{y + alto/2:.1f}" x2="{TAR_X}" '
            f'y2="{y + alto/2:.1f}" stroke="{P["rail"]}" stroke-width="1.25"/>')
        # la tarjeta
        piezas.append(
            f'<rect id="tarjeta-{i+1}" x="{TAR_X}" y="{y}" width="{w_tar:.0f}" '
            f'height="{alto}" rx="10" fill="{relleno}" stroke="{borde}" '
            f'stroke-width="1" filter="url(#dgSombra)"/>')

        # texto
        ty = y + PAD_Y + TAM + (0 if not sub else -1)
        color = P['fill'] if ultimo else P['text']
        for k, l in enumerate(lineas):
            piezas.append(
                f'<text x="{TAR_X+PAD_X}" y="{ty + k*INTER:.1f}" font-size="{TAM}" '
                f'font-weight="{600 if ultimo else 520}" fill="{color}">{_e(l)}</text>')
        if sub:
            piezas.append(
                f'<text x="{TAR_X+PAD_X}" y="{ty + len(lineas)*INTER + 1:.1f}" '
                f'font-size="11.5" font-weight="420" fill="{P["faint"]}">{_e(sub)}</text>')
        piezas.append('</g>')
        y += alto + HUECO

    alto_total = y - HUECO + 16

    # el riel, por detrás de los discos
    riel = [f'<line id="riel" x1="{RIEL_X}" y1="{centros[0]:.1f}" x2="{RIEL_X}" '
            f'y2="{centros[-1]:.1f}" stroke="url(#dgRiel)" stroke-width="2.5"/>']
    discos = []
    for i, cy in enumerate(centros):
        ultimo = i == len(centros) - 1
        discos.append(
            f'<circle cx="{RIEL_X}" cy="{cy:.1f}" r="{DISCO/2}" '
            f'fill="{P["accent"] if ultimo else P["fill"]}" '
            f'stroke="{P["accent"] if ultimo else P["rail"]}" stroke-width="1.5"/>')
        discos.append(
            f'<text x="{RIEL_X}" y="{cy+4.2:.1f}" font-size="12" font-weight="600" '
            f'text-anchor="middle" fill="{P["fill"] if ultimo else P["muted"]}">'
            f'{i+1}</text>')

    defs = f'''<defs>
    <linearGradient id="dgGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{P['fill']}"/>
      <stop offset="1" stop-color="{P['surface']}"/>
    </linearGradient>
    <linearGradient id="dgGradLlegada" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#0a7ab8"/>
      <stop offset="1" stop-color="{P['accent']}"/>
    </linearGradient>
    <linearGradient id="dgRiel" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{P['rail']}"/>
      <stop offset="0.55" stop-color="#8fc3d8"/>
      <stop offset="1" stop-color="{P['accent']}"/>
    </linearGradient>
    <filter id="dgSombra" x="-6%" y="-14%" width="112%" height="132%">
      <feDropShadow dx="0" dy="1.5" stdDeviation="2.2"
        flood-color="#0b3a56" flood-opacity="0.075"/>
    </filter>
  </defs>'''

    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{ancho}" '
            f'height="{alto_total:.0f}" viewBox="0 0 {ancho} {alto_total:.0f}" '
            f'role="img" font-family="{FUENTE}">{defs}'
            f'<g id="riel-grupo">{"".join(riel)}</g>'
            f'{"".join(piezas)}'
            f'<g id="discos">{"".join(discos)}</g></svg>')
