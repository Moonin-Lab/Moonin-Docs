"""Trazador propio de diagramas de secuencia.

d2 los dibujaba correctos pero con texto pequeño y uno desbordaba la columna. Como
los flowcharts, salen mejor dibujados a mano: los participantes son tarjetas, las
líneas de vida filetes finos, y cada mensaje va numerado sobre su flecha.

El mismo lenguaje visual que trazador.py —tarjetas con filete, acento en el borde,
Geist, tokens var(--dg-*)— para que los 52 diagramas se vean de la misma familia.
"""
import html
import re

P = {
    'text': '#0f172a', 'muted': '#475569', 'faint': '#64748b',
    'accent': '#0369a1', 'accent_dk': '#0b3a56', 'wash': '#e9f6fa',
    'hairline': '#dbe7eb', 'rail': '#cfe0e6', 'surface': '#f3fafb',
    'fill': '#ffffff', 'line': '#556577',
}
FUENTE = ("Geist, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, "
          "Helvetica, Arial, sans-serif")

_ESTRECHO = set('iljtfrI.,:;\'"|!()[]{}-/')
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


def leer_secuencia(codigo: str):
    """Participantes en orden y mensajes con su dirección y si son respuesta."""
    partes, orden, mensajes = {}, [], []
    for linea in codigo.splitlines():
        m = re.match(r'\s*participant\s+(\w+)(?:\s+as\s+(.+?))?\s*$', linea)
        if m:
            partes[m.group(1)] = (m.group(2) or m.group(1)).strip()
            orden.append(m.group(1))
            continue
        m = re.match(r'\s*(\w+)\s*(-?->>?|-->>|->>)\s*(\w+)\s*:\s*(.+?)\s*$', linea)
        if m:
            a, flecha, b, txt = m.groups()
            for n in (a, b):
                if n not in partes:
                    partes[n] = n
                    orden.append(n)
            mensajes.append((a, b, txt.strip(), flecha.startswith('--')))
    return orden, partes, mensajes


def trazar_secuencia_propia(codigo: str, ancho_max=636):
    orden, partes, mensajes = leer_secuencia(codigo)
    if not orden or not mensajes:
        return None

    TAM_P, TAM_M = 12.5, 12
    PAD, ALTO_CAB = 10, 44
    SEP = 46                      # separación vertical entre mensajes
    MARGEN_X, MARGEN_Y = 12, 14

    # ancho de columna: el que necesite la etiqueta más larga, acotado
    n = len(orden)
    col = min(168, max(104, (ancho_max - 2 * MARGEN_X) / n))
    ancho = round(2 * MARGEN_X + col * n)

    cx = {p: MARGEN_X + col * i + col / 2 for i, p in enumerate(orden)}
    # +18 de holgura: la etiqueta va ENCIMA de su flecha, así que el primer
    # mensaje necesita aire bajo las tarjetas o se monta sobre ellas.
    y0 = MARGEN_Y + ALTO_CAB + 18
    alto = round(y0 + SEP * len(mensajes) + 30)

    piezas = []

    # bandas alternas: dan ritmo de lectura sin dibujar una rejilla
    for i in range(len(mensajes)):
        if i % 2:
            piezas.append(
                f'<rect x="0" y="{y0 + SEP*i - 8:.0f}" width="{ancho}" height="{SEP}" '
                f'fill="var(--dg-surface, {P["surface"]})" opacity="0.55"/>')

    # líneas de vida
    for p in orden:
        piezas.append(
            f'<line x1="{cx[p]:.1f}" y1="{MARGEN_Y + ALTO_CAB:.0f}" x2="{cx[p]:.1f}" '
            f'y2="{alto - 16:.0f}" stroke="var(--dg-rail, {P["rail"]})" '
            f'stroke-width="1.25" stroke-dasharray="3 4"/>')

    # cabeceras de participante
    for i, p in enumerate(orden):
        x = MARGEN_X + col * i + 4
        w = col - 8
        etq = partes[p]
        lineas = _partir(etq, TAM_P, w - 12)[:2]
        piezas.append(
            f'<rect x="{x:.0f}" y="{MARGEN_Y}" width="{w:.0f}" height="{ALTO_CAB - 10}" '
            f'rx="8" fill="var(--dg-fill, {P["fill"]})" '
            f'stroke="var(--dg-border, {P["accent"]})" stroke-width="1.2"/>')
        ty = MARGEN_Y + (ALTO_CAB - 10) / 2 - (len(lineas) - 1) * 7 + 4
        for k, l in enumerate(lineas):
            piezas.append(
                f'<text x="{x + w/2:.1f}" y="{ty + k*14:.1f}" font-size="{TAM_P}" '
                f'font-weight="600" text-anchor="middle" '
                f'fill="var(--dg-text, {P["text"]})">{_e(l)}</text>')

    # mensajes
    for i, (a, b, txt, respuesta) in enumerate(mensajes):
        y = y0 + SEP * i + 16
        xa, xb = cx[a], cx[b]
        derecha = xb >= xa
        # la etiqueta va encima de su flecha, centrada en el tramo
        if a == b:
            lineas = _partir(txt, TAM_M, 128)[:2]
            for k, l in enumerate(lineas):
                piezas.append(
                    f'<text x="{xa + 34:.1f}" y="{y - 2 + k*13:.1f}" '
                    f'font-size="{TAM_M}" font-weight="450" text-anchor="start" '
                    f'fill="var(--dg-muted, {P["muted"]})">{_e(l)}</text>')
        else:
            lim = max(abs(xb - xa) - 18, 96)
            lineas = _partir(txt, TAM_M, lim)[:2]
            for k, l in enumerate(lineas):
                piezas.append(
                    f'<text x="{(xa + xb)/2:.1f}" y="{y - 8 - (len(lineas)-1-k)*13:.1f}" '
                    f'font-size="{TAM_M}" font-weight="450" text-anchor="middle" '
                    f'fill="var(--dg-muted, {P["muted"]})">{_e(l)}</text>')
        # el número del paso, sobre la línea de origen
        piezas.append(
            f'<circle cx="{xa:.1f}" cy="{y:.1f}" r="8" '
            f'fill="var(--dg-wash, {P["wash"]})" '
            f'stroke="var(--dg-border, {P["accent"]})" stroke-width="1"/>')
        piezas.append(
            f'<text x="{xa:.1f}" y="{y + 3.4:.1f}" font-size="9.5" font-weight="600" '
            f'text-anchor="middle" fill="var(--dg-border, {P["accent"]})">{i+1}</text>')
        guion = ' stroke-dasharray="5 4"' if respuesta else ''
        if a == b:
            # a sí mismo: un bucle a la derecha. Una línea de largo cero no se ve.
            r, bx = 13, xa + 9
            piezas.append(
                f'<path d="M{bx:.1f} {y-6:.1f} h{r} a7 7 0 0 1 0 14 h{-r}" '
                f'fill="none" stroke="var(--dg-line, {P["line"]})" '
                f'stroke-width="1.4"{guion}/>')
            piezas.append(
                f'<path d="M{bx:.1f} {y+8:.1f} l6 -3.6 l0 7.2 z" '
                f'fill="var(--dg-line, {P["line"]})"/>')
        else:
            d = 1 if derecha else -1
            x1 = xa + d * 9
            x2 = xb - d * 5
            piezas.append(
                f'<line x1="{x1:.1f}" y1="{y:.1f}" x2="{x2:.1f}" y2="{y:.1f}" '
                f'stroke="var(--dg-line, {P["line"]})" stroke-width="1.4"{guion}/>')
            piezas.append(
                f'<path d="M{x2:.1f} {y:.1f} l{-d*6:.1f} -3.6 l0 7.2 z" '
                f'fill="var(--dg-line, {P["line"]})"/>')

    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{ancho}" height="{alto}" '
            f'viewBox="0 0 {ancho} {alto}" role="img" font-family="{FUENTE}">'
            f'{"".join(piezas)}</svg>')
