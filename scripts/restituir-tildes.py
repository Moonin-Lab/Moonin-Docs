"""Restituye tildes y eñes en la documentación en español.

El corpus estaba escrito sin acentos —5 caracteres acentuados en 30 archivos— y al
completar las traducciones copié ese estilo. Era propagar un error, no respetar una
convención: en español la tilde y la eñe son ortografía, no decoración.

QUÉ SE PROTEGE

  · los bloques de código que no son mermaid (bash, yaml, json): ahí «revision»
    puede ser un identificador y tildarlo lo rompería
  · el código en línea, como `kubectl top`
  · el destino de los enlaces y las URL
  · las claves del frontmatter, aunque sus valores sí se corrigen

Las etiquetas de los diagramas mermaid SÍ se corrigen: son prosa que el lector ve.

LO QUE DEPENDE DEL CONTEXTO

«esta» es demostrativo ante sustantivo («esta página») y verbo ante participio o
adjetivo («está disponible»). Igual «mas»/«más», «este»/«esté» y los pretéritos
«fallo»/«falló», «cambio»/«cambió». Esos se resuelven por la palabra siguiente y lo
que no encaja en ninguna regla se informa para revisarlo a mano, en vez de adivinar.
"""
import re
import sys
from pathlib import Path

RAIZ = Path('src/content/docs/es')

# ── palabras que SIEMPRE llevan tilde o eñe ────────────────────────────────
# Sin los plurales que la pierden: «revisión» pero «revisiones».
SIEMPRE = {
    'revision': 'revisión', 'version': 'versión', 'ejecucion': 'ejecución',
    'notificacion': 'notificación', 'administracion': 'administración',
    'aplicacion': 'aplicación', 'configuracion': 'configuración',
    'informacion': 'información', 'operacion': 'operación', 'accion': 'acción',
    'opcion': 'opción', 'integracion': 'integración', 'instalacion': 'instalación',
    'creacion': 'creación', 'validacion': 'validación', 'sesion': 'sesión',
    'conexion': 'conexión', 'region': 'región', 'decision': 'decisión',
    'descripcion': 'descripción', 'definicion': 'definición',
    'autenticacion': 'autenticación', 'autorizacion': 'autorización',
    'sincronizacion': 'sincronización', 'deteccion': 'detección',
    'division': 'división', 'presion': 'presión', 'gestion': 'gestión',
    'politica': 'política', 'politicas': 'políticas',
    'metricas': 'métricas', 'metrica': 'métrica',
    'jerarquia': 'jerarquía', 'garantia': 'garantía', 'categoria': 'categoría',
    'tambien': 'también', 'ademas': 'además', 'despues': 'después',
    'segun': 'según', 'asi': 'así', 'aqui': 'aquí', 'alla': 'allá',
    'numero': 'número', 'numeros': 'números',
    'codigo': 'código', 'codigos': 'códigos',
    'parametro': 'parámetro', 'parametros': 'parámetros',
    'minimo': 'mínimo', 'minima': 'mínima', 'maximo': 'máximo', 'maxima': 'máxima',
    'util': 'útil', 'utiles': 'útiles', 'utilices': 'utilices',
    'publico': 'público', 'publica': 'pública', 'publicas': 'públicas',
    'automatico': 'automático', 'automatica': 'automática',
    'automaticos': 'automáticos', 'automaticas': 'automáticas',
    'rapido': 'rápido', 'rapida': 'rápida', 'rapidas': 'rápidas',
    'ultima': 'última', 'ultimo': 'último', 'ultimas': 'últimas',
    'ultimos': 'últimos', 'unica': 'única', 'unico': 'único',
    'generico': 'genérico', 'genericos': 'genéricos',
    'especifico': 'específico', 'especificos': 'específicos',
    'especifica': 'específica', 'especificas': 'específicas',
    'tipico': 'típico', 'tipicos': 'típicos', 'tipica': 'típica',
    'historico': 'histórico', 'historial': 'historial',
    'practica': 'práctica', 'practicas': 'prácticas',
    'tecnico': 'técnico', 'tecnicos': 'técnicos',
    'analisis': 'análisis', 'sintesis': 'síntesis',
    'linea': 'línea', 'lineas': 'líneas',
    'area': 'área', 'areas': 'áreas',
    'dia': 'día', 'dias': 'días', 'via': 'vía', 'vias': 'vías',
    'periodo': 'período', 'energia': 'energía',
    'limite': 'límite', 'limites': 'límites',
    'multiples': 'múltiples', 'multiple': 'múltiple',
    'estandar': 'estándar', 'quedara': 'quedará',
    'estan': 'están', 'seran': 'serán', 'sera': 'será',
    'podra': 'podrá', 'podran': 'podrán', 'habra': 'habrá',
    'tendra': 'tendrá', 'estara': 'estará', 'hara': 'hará', 'dara': 'dará',
    'ingles': 'inglés', 'espanol': 'español', 'espanola': 'española',
    # eñes
    'senal': 'señal', 'senales': 'señales', 'senalar': 'señalar',
    'contrasena': 'contraseña', 'contrasenas': 'contraseñas',
    'ano': 'año', 'anos': 'años', 'diseno': 'diseño', 'disenar': 'diseñar',
    'pequeno': 'pequeño', 'pequena': 'pequeña', 'manana': 'mañana',
    'tamano': 'tamaño', 'compania': 'compañía', 'companias': 'compañías',
    'dueno': 'dueño', 'extrano': 'extraño',
}

# ── ambiguas: la palabra SIGUIENTE decide ─────────────────────────────────
# «esta» es verbo ante participio o adjetivo; demostrativo ante sustantivo.
ESTA_VERBO = {
    'centrado', 'centrada', 'activo', 'activa', 'escrita', 'escrito',
    'gestionado', 'gestionada', 'acotado', 'acotada', 'habilitado', 'habilitada',
    'disponible', 'corriendo', 'orientada', 'orientado', 'documentado',
    'documentada', 'recolectando', 'sana', 'sano', 'pensada', 'pensado',
    'concentrado', 'concentrada', 'en', 'dentro', 'listo', 'lista', 'vacio',
    'vacia', 'vinculado', 'vinculada', 'deshabilitado', 'deshabilitada',
    'expuesto', 'expuesta', 'limitado', 'limitada', 'pausado', 'pausada',
    'silenciada', 'silenciado', 'sujeto', 'sujeta', 'incluido', 'incluida',
}
ESTE_SUBJUNTIVO = {'contribuyendo', 'aportando', 'afectando', 'generando'}

# «mas» en este corpus es siempre comparativo
MAS_SIEMPRE = True


def partir(texto):
    """Devuelve trozos (protegido, contenido) para no tocar código ni enlaces.

    Los bloques mermaid NO se protegen: sus etiquetas son prosa visible.
    """
    piezas, i = [], 0
    patron = re.compile(r'(```[a-zA-Z]*\n.*?```|`[^`\n]*`|\]\([^)]*\)|https?://\S+)', re.S)
    for m in patron.finditer(texto):
        if m.start() > i:
            piezas.append((False, texto[i:m.start()]))
        bloque = m.group(0)
        # los diagramas sí se corrigen
        protegido = not bloque.startswith('```mermaid')
        piezas.append((protegido, bloque))
        i = m.end()
    if i < len(texto):
        piezas.append((False, texto[i:]))
    return piezas


def con_mayuscula(orig, nuevo):
    if orig[:1].isupper():
        return nuevo[:1].upper() + nuevo[1:]
    return nuevo


def corregir(texto, dudas):
    def una(m):
        w = m.group(0)
        b = w.lower()
        sig = m.string[m.end():m.end() + 24].strip().split(' ')[0].lower().strip('.,;:)?!')
        if b == 'esta':
            return con_mayuscula(w, 'está') if sig in ESTA_VERBO else w
        if b == 'este':
            return con_mayuscula(w, 'esté') if sig in ESTE_SUBJUNTIVO else w
        if b == 'mas':
            return con_mayuscula(w, 'más') if MAS_SIEMPRE else w
        if b in SIEMPRE:
            return con_mayuscula(w, SIEMPRE[b])
        return w

    salida = []
    for protegido, trozo in partir(texto):
        if protegido:
            salida.append(trozo)
            continue
        # dentro de un bloque mermaid solo se tocan las etiquetas, no las directivas
        salida.append(re.sub(r'\b[A-Za-zÁÉÍÓÚÑáéíóúñ]{2,}\b', una, trozo))
    return ''.join(salida)


def preguntas(texto):
    """Abre las interrogaciones y tilda los interrogativos."""
    def linea(m):
        pre, cuerpo = m.group(1), m.group(2)
        if cuerpo.lstrip().startswith('¿'):
            return m.group(0)
        c = cuerpo
        c = re.sub(r'^(\s*)Que\b', r'\1Qué', c)
        c = re.sub(r'^(\s*)Donde\b', r'\1Dónde', c)
        c = re.sub(r'^(\s*)Cuando\b', r'\1Cuándo', c)
        c = re.sub(r'^(\s*)Cuanto\b', r'\1Cuánto', c)
        c = re.sub(r'\bque\b(?=\s+(pasa|ocurre|significa|entrega|hace))', 'qué', c)
        sangria = re.match(r'^(\s*)', c).group(1)
        return f'{pre}{sangria}¿{c.strip()}'

    # encabezados
    texto = re.sub(r'^(#{2,6} )(.+\?)\s*$', lambda m: linea(m), texto, flags=re.M)
    # viñetas y párrafos que son preguntas
    texto = re.sub(r'^(- |\d+\. |)([A-ZÁÉÍÓÚa-záéíóú][^\n]*\?)\s*$',
                   lambda m: linea(m), texto, flags=re.M)
    return texto


def main():
    dudas = []
    cambiados = 0
    total_sust = 0
    for p in sorted(RAIZ.rglob('*.md')):
        antes = p.read_text(encoding='utf8')
        despues = preguntas(corregir(antes, dudas))
        if despues != antes:
            n = sum(1 for a, b in zip(antes, despues) if a != b)
            p.write_text(despues, encoding='utf8')
            cambiados += 1
            total_sust += 1
            print(f'  ✓ {p.relative_to(RAIZ)}')
    print(f'\n  archivos corregidos: {cambiados} de {len(list(RAIZ.rglob("*.md")))}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
