"""Completa las traducciones al español usando el inglés como fuente de verdad.

Determinado por medición: de los 30 pares, 9 tienen más contenido en inglés y NINGUNO
tiene contenido exclusivo en español. Si el español fuera la fuente habría al menos
uno. Así que el inglés es la fuente y el español una traducción incompleta.

Estilo del español existente, respetado aquí:
  · SIN acentos (en todo el corpus español hay 5 caracteres acentuados)
  · cabeceras de tabla en minúscula, no en mayúsculas
  · los términos técnicos se dejan en inglés: Deployments, CronJobs, HPA, rollback
  · viñetas en minúscula

Invariantes de producto que se respetan al traducir:
  · 16 herramientas MCP, de solo lectura
  · no hay remediación automática; la única mutación es HPA y réplicas del Scaling
    Rules Agent, opcional y desactivada
  · ArgoCD solo DETECTA la anotación
"""
from pathlib import Path

RAIZ = Path('src/content/docs/es')

# ─────────────────── lo que se agrega a cada archivo ───────────────────
# (ruta, texto que precede al punto de inserción o None para agregar al final, bloque)

ARQ_DIAGRAMA = '''
```mermaid
graph TB
    subgraph "Tu infraestructura"
        K8S[Cluster de Kubernetes]
        DISCOVERY[Discovery Agent]
        SCALING[Scaling Rules Agent]
        DISCOVERY -.->|Observa| K8S
        SCALING -.->|Reconcilia HPAs| K8S
    end

    subgraph "Plataforma Moonin"
        API[API de control]
        DI[API de ingesta de datos]
        FRONT[Aplicacion web]
        ADMIN[Consola de administracion]
        MCP[Servidor MCP]
        NOTIFIER[Motor de notificaciones]
        SCALINGAPI[API de scaling rules]
    end

    subgraph "Integraciones externas"
        GH[GitHub]
        ACD[ArgoCD]
        SLACK[Slack]
        TEAMS[Microsoft Teams]
        VOPS[VictorOps]
        AI[Herramientas de IA / clientes MCP]
    end

    DISCOVERY -->|HTTPS + token| API
    DISCOVERY -->|HTTPS + token| DI
    SCALING -->|HTTPS + token| SCALINGAPI
    FRONT -->|Proxy| API
    FRONT -->|Proxy| DI
    FRONT -->|Proxy| SCALINGAPI
    ADMIN -->|Proxy| API
    NOTIFIER --> SLACK
    NOTIFIER --> TEAMS
    NOTIFIER --> VOPS
    GH -.->|Webhooks| API
    ACD -.->|Webhooks| API
    MCP --> AI
    USERS[Usuarios] -->|Navegador| FRONT
    ADMINS[Administradores] -->|Navegador| ADMIN
```
'''

ARQ_COLA = '''
### Motor de notificaciones

Un worker en segundo plano que evalua las alert policies y las event notification
policies, y despacha las notificaciones a los canales configurados con horarios,
control de ritmo y silencios.

## Flujos de datos

### Seguimiento de deployments

```mermaid
sequenceDiagram
    participant Agent as Discovery Agent
    participant API as API de control
    participant DB as Almacen de datos
    participant Front as Aplicacion web

    Agent->>API: Detecta cambio de Deployment
    API->>DB: Guarda revision e imagenes
    API->>API: Vincula incidentes y contexto del rollout
    Front->>API: Pide datos del deployment
    API->>Front: Devuelve revisiones y estado vinculado
```

### Inventario de cluster y flujo de CronJobs

```mermaid
sequenceDiagram
    participant Agent as Discovery Agent
    participant API as API de control
    participant DB as Almacen de datos
    participant Front as Aplicacion web

    Agent->>API: Envia heartbeat de metadata del cluster
    Agent->>API: Actualiza snapshots de nodos
    Agent->>API: Sincroniza CronJobs y ejecuciones de Jobs
    API->>DB: Persiste inventario e historial de ejecuciones
    Front->>API: Consulta clusters, nodos y CronJobs
    API->>Front: Devuelve el inventario filtrado
```

### Ejecucion de scaling y rollback

```mermaid
sequenceDiagram
    participant User as Usuario / API
    participant Scaling as Scaling Rules Agent
    participant K8S as API de Kubernetes
    participant API as API de scaling rules

    User->>API: Crea o deshabilita una scaling rule
    API->>Scaling: Reconcilia el estado activo
    Scaling->>K8S: Aplica valores temporales de HPA
    Scaling->>API: Guarda el estado de rollback
    API->>Scaling: Regla deshabilitada o expirada
    Scaling->>K8S: Restaura el estado previo del HPA
```

## Modelo de autenticacion

- los usuarios se autentican con Google OAuth o con correo y contrasena
- los agentes se autentican con un token propio del cluster
- las aplicaciones web hacen proxy de las llamadas al backend del lado del servidor
- el servidor MCP expone tokens de acceso de solo lectura y con alcance acotado

## Modelo de almacenamiento

- la metadata de organizaciones, proyectos, clusters, revisiones, snapshots de nodos
  y CronJobs se guarda en una base de datos relacional
- los extractos de log de los CronJobs que fallan se guardan junto al registro de la
  ejecucion
- las metricas agregadas y los resumenes se guardan aparte para que los tableros
  respondan rapido

## Aspectos de seguridad

- toda la comunicacion de los agentes usa HTTPS
- los tokens de cluster se comparan en tiempo constante
- el navegador nunca recibe tokens internos de la API
- los manifiestos sanitizados conservan la identidad de los recursos, como el nombre
  de un Secret, y ocultan solo los valores sensibles
'''

RCA_COLA = '''
## Preguntas utiles para el operador

- el problema empezo despues de un rollout?
- hay un job programado que fallo y este contribuyendo al incidente?
- el problema esta acotado a un cluster o es mas amplio?
- una scaling rule temporal cambio la capacidad poco antes del incidente?

## Flujo recomendado

1. partir del error activo o del workload
2. revisar la ultima revision y la actividad reciente de CronJobs
3. revisar el contexto de cluster y de nodos
4. confirmar si una policy, un silencio o una accion de scaling cambio el camino de
   la respuesta
'''

OVERVIEW_COLA = '''
## Aplicaciones principales

| Aplicacion | Para que sirve |
|---|---|
| `app.moonin.app` | Espacio principal de ingenieria: tableros, workloads, revisiones, errores y policies |
| `app-admin.moonin.app` | Consola de administracion de organizaciones, proyectos, clusters y canales de notificacion |
| `api-discover.moonin.app` | API de control que usan los agentes y las aplicaciones web |
| `api-scaling-rules.moonin.app` | Plano de control de las scaling rules |
| `mcp.moonin.app` | Superficie MCP de solo lectura para herramientas y asistentes de IA |

## Areas de la plataforma que reflejan estos documentos

- tablero de overview con senales compactas de salud e inventario
- pagina dedicada de inventario de nodos, con filas expandibles y adaptables
- pagina de CronJobs con historial de ejecuciones y horarios legibles
- mejores enlaces directos a las consolas de AWS y GCP desde el frontend
- event notification policies y la experiencia de horarios por canal
- chart del agente que empaqueta el Discovery Agent y el Scaling Rules Agent

## Quien usa Moonin

- ingenieria de plataforma que administra entornos multi-cluster
- equipos de SRE que revisan el impacto de un rollout y los incidentes activos
- equipos de DevOps que estandarizan notificaciones y comportamiento de scaling
- equipos de aplicacion que validan imagenes, CronJobs e historial de despliegue
'''

INICIO_COLA = '''
## Areas actuales del producto

| Area | Que entrega |
|---|---|
| Tablero de overview | Vista ejecutiva de revisiones, imagenes, clusters, CronJobs y senales de falla |
| Clusters | Conectividad, cloud metadata, enlaces directos al proveedor e inventario de namespaces |
| Nodos | Snapshots de capacidad y asignable, condiciones y topologia del cluster |
| Deployments | Historial de rollouts, imagenes, contexto de Helm e incidentes vinculados |
| CronJobs | Horarios legibles, ejecuciones en vivo y logs de los jobs que fallaron |
| Policies | Alert policies, event notifications, silencios y gobierno de las scaling rules |

## Necesitas ingles?

La version completa en ingles esta disponible en [English](../getting-started/).
'''

INTEGRACIONES_COLA = '''
## Por que importan las integraciones

- enriquecen el historial de rollouts con contexto de entrega
- alinean los cambios del cluster con Git y con los sistemas de despliegue
- estandarizan la gestion de acceso de los equipos de ingenieria
'''

QUICKSTART_COLA = '''
### 6. Configurar las policies de respuesta

Crear o actualizar:

- **Alert Policies** para las senales de error
- **Event Notification Policies** para eventos de despliegue o de plataforma

Los canales de notificacion se crean en la **Consola de administracion** y despues se
eligen desde la aplicacion principal.
'''

FAQ_COLA = '''
## Moonin conserva los nombres de los Secrets en los manifiestos sanitizados?

Si. Los valores sensibles se ocultan, pero la identidad de los recursos —como el
nombre de un Secret— se conserva para dar contexto al diagnostico.
'''

GITHUB_COLA = '''
## Buenas practicas

- usar una convencion de nombres de repositorio consistente entre equipos
- alinear los nombres de deployment con los nombres de proyecto cuando sea posible
'''

INDEX_CABEZA = '''## Que conecta Moonin

Moonin es una plataforma de operaciones para Kubernetes centrada en cinco trabajos
conectados:

- modelar la jerarquia de runtime de tu parque
- registrar cada rollout como una revision
- capturar las fallas de runtime con el contexto del rollout
- enrutar las notificaciones a traves de policies reutilizables
- mantener gobernados desde un solo lugar el acceso, los clusters y los canales

Esta documentacion esta escrita para que un operador pueda ir del alta a la operacion
diaria sin depender de conocimiento de producto que no este escrito.

'''

AL_FINAL = [
    ('getting-started/architecture.md', ARQ_COLA),
    ('rca/index.md', RCA_COLA),
    ('getting-started/overview.md', OVERVIEW_COLA),
    ('getting-started/index.md', INICIO_COLA),
    ('integrations/index.md', INTEGRACIONES_COLA),
    ('getting-started/quickstart.md', QUICKSTART_COLA),
    ('faq/index.md', FAQ_COLA),
    ('integrations/github.md', GITHUB_COLA),
]


def main():
    # 1. el diagrama de la vista general, que faltaba en una seccion ya existente
    p = RAIZ / 'getting-started' / 'architecture.md'
    s = p.read_text(encoding='utf8')
    assert '```mermaid' not in s, 'ya tiene diagramas'
    ancla = '## Componentes principales'
    assert s.count(ancla) == 1
    s = s.replace(ancla, ARQ_DIAGRAMA.strip() + '\n\n' + ancla)
    p.write_text(s, encoding='utf8')
    print('  ✓ architecture.md: diagrama de la vista general')

    # 2. la seccion de apertura de index.md, que va ANTES de lo que ya existe
    p = RAIZ / 'index.md'
    s = p.read_text(encoding='utf8')
    ancla = '## Entradas por idioma'
    assert s.count(ancla) == 1
    s = s.replace(ancla, INDEX_CABEZA + ancla)
    p.write_text(s, encoding='utf8')
    print('  ✓ index.md: seccion de apertura')

    # 3. el resto se agrega al final, en el orden del ingles
    for rel, bloque in AL_FINAL:
        p = RAIZ / rel
        s = p.read_text(encoding='utf8').rstrip()
        p.write_text(s + '\n' + bloque.rstrip() + '\n', encoding='utf8')
        print(f'  ✓ {rel}')


if __name__ == '__main__':
    main()
