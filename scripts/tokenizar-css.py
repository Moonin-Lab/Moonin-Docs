"""Tokeniza portal.css para que el tema oscuro sea posible.

El problema: 117 colores clavados en 66 de los 98 bloques. Aunque se defina una
paleta oscura en el :root, dos tercios de la hoja la ignoran. Por eso el conmutador
de tema de Starlight estaba presente en el HTML pero no cambiaba nada.

Cada color se lleva a un token semántico por su PAPEL, no por su valor, y después
cada token recibe un valor para claro y otro para oscuro, homologados a los del
sitio (front/src/App.css).

La barra superior también se homologa: la documentación la tenía oscura (#0b1118)
mientras la del sitio es blanca en tema claro. Ahora sigue al tema.
"""
import re
from collections import Counter
from pathlib import Path

CSS = Path('src/styles/portal.css')

# color clavado → token semántico, agrupado por PAPEL
MAPA = {
    # superficies
    '#ffffff': '--p-surface',
    '#f8fdff': '--p-surface-2', '#f8fcff': '--p-surface-2',
    '#f0f9ff': '--p-surface-2', '#e7f5ff': '--p-surface-2',
    '#f3fafb': '--p-surface-2', '#f8fafc': '--p-surface-2',
    '#f1f5f9': '--p-surface-2', '#f0f4f8': '--p-surface-2',
    # filetes
    '#e2e8f0': '--p-line', '#eaf0f6': '--p-line', '#dbe6f3': '--p-line',
    '#e5e7eb': '--p-line', '#cbd5e1': '--p-line-strong',
    # texto
    '#0f172a': '--p-text',
    '#334155': '--p-text-2', '#1e293b': '--p-text-2', '#475569': '--p-text-2',
    '#64748b': '--p-text-3', '#a7b4c2': '--p-text-3',
    # acento
    '#0ea5e9': '--p-accent', '#0284c7': '--p-accent', '#0369a1': '--p-accent',
    '#38bdf8': '--p-accent-hi', '#7dd3fc': '--p-accent-line',
    '#e0f2fe': '--p-accent-wash', '#eff6ff': '--p-accent-wash',
    '#dbeafe': '--p-accent-wash',
    '#0c4a6e': '--p-accent-deep', '#075985': '--p-accent-deep',
    '#082f49': '--p-accent-deep',
    # la barra superior y sus tonos
    '#0b1118': '--p-bar',
    '#132131': '--p-bar-2', '#12213a': '--p-bar-2', '#0e1d33': '--p-bar-2',
    '#24303d': '--p-bar-3', '#22375a': '--p-bar-3', '#1b2a44': '--p-bar-3',
    '#1f3251': '--p-bar-3', '#163752': '--p-bar-3', '#243b52': '--p-bar-3',
    '#67e8f9': '--p-bar-accent', '#22d3ee': '--p-bar-accent',
    '#e6eefb': '--p-bar-text', '#9fb3cc': '--p-bar-text-2',
    '#3b4f6e': '--p-bar-line', '#4d6890': '--p-bar-line',
    # estados
    '#f0fdf4': '--p-ok-wash', '#34d399': '--p-ok',
    '#fffbeb': '--p-warn-wash', '#fbbf24': '--p-warn',
    '#fff1f2': '--p-bad-wash', '#fb7185': '--p-bad',
}

MAPA_RGBA = {
    'rgba(15, 23, 42, 0.05)': '--p-shadow-sm',
    'rgba(15, 23, 42, 0.08)': '--p-shadow-md',
    'rgba(15, 23, 42, 0.12)': '--p-shadow-lg',
    'rgba(15, 23, 42, 0.2)': '--p-shadow-xl',
    'rgba(2, 8, 23, 0.24)': '--p-bar-shadow',
    'rgba(3, 105, 161, 0.09)': '--p-halo',
    'rgba(103, 232, 249, 0.16)': '--p-bar-line-soft',
    'rgba(103, 232, 249, 0.55)': '--p-bar-accent-strong',
    'rgba(103, 232, 249, 0.28)': '--p-bar-accent-soft',
    'rgba(103, 232, 249, 0.18)': '--p-bar-accent-faint',
    'rgba(34, 211, 238, 0.1)': '--p-bar-accent-wash',
    'rgba(34, 211, 238, 0.14)': '--p-bar-accent-wash-2',
    'rgba(14, 165, 233, 0.22)': '--p-accent-ring',
    'rgba(2, 132, 199, 0.35)': '--p-accent-ring-strong',
    'rgba(186, 230, 253, 0.28)': '--p-accent-line-soft',
    'rgba(186, 230, 253, 0.3)': '--p-accent-line-soft',
    'rgba(255, 255, 255, 0.94)': '--p-surface-veil',
    'rgba(255, 255, 255, 0.06)': '--p-veil',
}

# valores por tema. Los del sitio para lo compartido; los propios donde la
# documentación tiene elementos que el sitio no tiene.
CLARO = {
    '--p-surface': '#ffffff', '--p-surface-2': '#f3fafb',
    '--p-line': '#dbe7eb', '--p-line-strong': '#b9cbd1',
    '--p-text': '#0f172a', '--p-text-2': '#334155', '--p-text-3': '#556577',
    '--p-accent': '#0369a1', '--p-accent-hi': '#0a7ab8',
    '--p-accent-line': '#a8d3e4', '--p-accent-wash': '#e9f6fa',
    '--p-accent-deep': '#0b3a56',
    # en claro la barra es blanca, como la del sitio
    '--p-bar': '#ffffff', '--p-bar-2': '#f3fafb', '--p-bar-3': '#e9f2f4',
    '--p-bar-accent': '#0369a1', '--p-bar-text': '#0f172a',
    '--p-bar-text-2': '#556577', '--p-bar-line': '#dbe7eb',
    '--p-ok': '#047857', '--p-ok-wash': '#ecfdf5',
    '--p-warn': '#b45309', '--p-warn-wash': '#fffbeb',
    '--p-bad': '#c81e1e', '--p-bad-wash': '#fef2f2',
    '--p-shadow-sm': 'rgba(11, 58, 86, 0.05)',
    '--p-shadow-md': 'rgba(11, 58, 86, 0.08)',
    '--p-shadow-lg': 'rgba(11, 58, 86, 0.12)',
    '--p-shadow-xl': 'rgba(11, 58, 86, 0.18)',
    '--p-bar-shadow': 'rgba(11, 58, 86, 0.07)',
    '--p-halo': 'rgba(3, 105, 161, 0.09)',
    '--p-bar-line-soft': 'rgba(3, 105, 161, 0.14)',
    '--p-bar-accent-strong': 'rgba(3, 105, 161, 0.55)',
    '--p-bar-accent-soft': 'rgba(3, 105, 161, 0.24)',
    '--p-bar-accent-faint': 'rgba(3, 105, 161, 0.14)',
    '--p-bar-accent-wash': 'rgba(3, 105, 161, 0.08)',
    '--p-bar-accent-wash-2': 'rgba(3, 105, 161, 0.12)',
    '--p-accent-ring': 'rgba(3, 105, 161, 0.22)',
    '--p-accent-ring-strong': 'rgba(3, 105, 161, 0.35)',
    '--p-accent-line-soft': 'rgba(168, 211, 228, 0.4)',
    '--p-surface-veil': 'rgba(255, 255, 255, 0.94)',
    '--p-veil': 'rgba(11, 58, 86, 0.05)',
}

OSCURO = {
    # los tonos del sitio en oscuro
    '--p-surface': '#0e1a2e', '--p-surface-2': '#13203a',
    '--p-line': 'rgba(148, 163, 184, 0.16)',
    '--p-line-strong': 'rgba(148, 163, 184, 0.3)',
    '--p-text': '#e9eefb', '--p-text-2': '#a9b9d1', '--p-text-3': '#8798b2',
    '--p-accent': '#22d3ee', '--p-accent-hi': '#67e8f9',
    '--p-accent-line': 'rgba(34, 211, 238, 0.24)',
    '--p-accent-wash': 'rgba(34, 211, 238, 0.10)',
    '--p-accent-deep': '#a5f3fc',
    '--p-bar': '#0a1424', '--p-bar-2': '#0e1a2e', '--p-bar-3': '#13203a',
    '--p-bar-accent': '#22d3ee', '--p-bar-text': '#e9eefb',
    '--p-bar-text-2': '#a9b9d1',
    '--p-bar-line': 'rgba(148, 163, 184, 0.16)',
    '--p-ok': '#34d399', '--p-ok-wash': 'rgba(52, 211, 153, 0.12)',
    '--p-warn': '#fbbf24', '--p-warn-wash': 'rgba(251, 191, 36, 0.12)',
    '--p-bad': '#fb7185', '--p-bad-wash': 'rgba(251, 113, 133, 0.14)',
    '--p-shadow-sm': 'rgba(0, 0, 0, 0.5)',
    '--p-shadow-md': 'rgba(0, 0, 0, 0.5)',
    '--p-shadow-lg': 'rgba(0, 0, 0, 0.6)',
    '--p-shadow-xl': 'rgba(0, 0, 0, 0.7)',
    '--p-bar-shadow': 'rgba(0, 0, 0, 0.5)',
    '--p-halo': 'rgba(34, 211, 238, 0.10)',
    '--p-bar-line-soft': 'rgba(34, 211, 238, 0.16)',
    '--p-bar-accent-strong': 'rgba(103, 232, 249, 0.55)',
    '--p-bar-accent-soft': 'rgba(103, 232, 249, 0.28)',
    '--p-bar-accent-faint': 'rgba(103, 232, 249, 0.18)',
    '--p-bar-accent-wash': 'rgba(34, 211, 238, 0.10)',
    '--p-bar-accent-wash-2': 'rgba(34, 211, 238, 0.14)',
    '--p-accent-ring': 'rgba(34, 211, 238, 0.24)',
    '--p-accent-ring-strong': 'rgba(34, 211, 238, 0.4)',
    '--p-accent-line-soft': 'rgba(34, 211, 238, 0.2)',
    '--p-surface-veil': 'rgba(14, 26, 46, 0.94)',
    '--p-veil': 'rgba(255, 255, 255, 0.06)',
}

# tokens de diagrama, que hacen que los 52 SVG sigan el tema
DG_CLARO = {
    '--dg-fill': '#ffffff', '--dg-surface': '#f3fafb', '--dg-surface-2': '#eef7f9',
    '--dg-hairline': '#dbe7eb', '--dg-border': '#0369a1', '--dg-line': '#556577',
    '--dg-text': '#0f172a', '--dg-muted': '#475569', '--dg-faint': '#64748b',
    '--dg-wash': '#e9f6fa', '--dg-accent-hi': '#0a7ab8', '--dg-accent-dk': '#0b3a56',
    '--dg-rail': '#cfe0e6', '--dg-rail-mid': '#8fc3d8',
}
DG_OSCURO = {
    '--dg-fill': '#13203a', '--dg-surface': '#0e1a2e', '--dg-surface-2': '#182a49',
    '--dg-hairline': 'rgba(148, 163, 184, 0.22)', '--dg-border': '#22d3ee',
    '--dg-line': '#8798b2', '--dg-text': '#e9eefb', '--dg-muted': '#a9b9d1',
    '--dg-faint': '#8798b2', '--dg-wash': 'rgba(34, 211, 238, 0.12)',
    '--dg-accent-hi': '#67e8f9', '--dg-accent-dk': '#0a1424',
    '--dg-rail': 'rgba(148, 163, 184, 0.28)', '--dg-rail-mid': 'rgba(34, 211, 238, 0.5)',
}


def main():
    s = CSS.read_text(encoding='utf8')
    fin_root = re.search(r'^:root,.*?\n\}\n', s, re.S).end()
    root, resto = s[:fin_root], s[fin_root:]

    # normalizar rgba para que coincidan con las claves
    def norm(m):
        nums = re.findall(r'[\d.]+', m.group(0))
        pre = 'rgba' if len(nums) == 4 else 'rgb'
        return f'{pre}({", ".join(nums)})'
    resto = re.sub(r'rgba?\([^)]*\)', norm, resto)

    sin_mapear = Counter()
    n = 0
    for col, tok in sorted(MAPA.items(), key=lambda x: -len(x[0])):
        for forma in (col, col.upper()):
            c = len(re.findall(re.escape(forma) + r'\b', resto))
            if c:
                resto = re.sub(re.escape(forma) + r'\b', f'var({tok})', resto)
                n += c
    for col, tok in MAPA_RGBA.items():
        c = resto.count(col)
        if c:
            resto = resto.replace(col, f'var({tok})')
            n += c
    for x in re.findall(r'#[0-9a-fA-F]{3,8}|rgba?\([^)]*\)', resto):
        sin_mapear[x.lower()] += 1

    def bloque(nombre, sel, *mapas):
        L = [f'/* ── {nombre} ── */', sel + ' {']
        for m in mapas:
            for k, v in m.items():
                L.append(f'  {k}: {v};')
        L.append('}')
        return '\n'.join(L)

    paletas = (
        '\n\n/* ═══════════════ paletas ═══════════════\n'
        '   Los valores son los del sitio (front/src/App.css) para que los dos\n'
        '   soportes se vean del mismo sistema. Starlight ya persiste la elección y\n'
        '   cae a prefers-color-scheme cuando el usuario no ha elegido, así que la\n'
        '   detección automática del sistema sale de su propio conmutador.\n'
        '   ══════════════════════════════════════ */\n\n'
        + bloque('claro', ':root, :root[data-theme="light"]', CLARO, DG_CLARO)
        + '\n\n'
        + bloque('oscuro', ':root[data-theme="dark"]', OSCURO, DG_OSCURO)
        + '\n'
    )

    CSS.write_text(root + paletas + resto, encoding='utf8')
    print(f'  colores llevados a token: {n}')
    print(f'  sin mapear: {len(sin_mapear)}')
    for c, k in sin_mapear.most_common(12):
        print(f'    {k}×  {c}')


if __name__ == '__main__':
    main()
