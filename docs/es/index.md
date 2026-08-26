# Documentacion de Moonin

Moonin es una plataforma de operaciones para Kubernetes centrada en cinco trabajos conectados:

- modelar la jerarquia runtime del estate
- seguir cada rollout como una revision
- capturar fallas runtime con contexto de cambio
- enrutar notificaciones usando politicas reutilizables
- gobernar acceso, clusters y canales desde una sola capa administrativa

Esta documentacion esta escrita para que un operador pueda pasar desde el onboarding hasta la operacion diaria sin depender de conocimiento oculto del producto.

## Entradas por idioma

| Idioma | Punto de inicio |
|---|---|
| Espanol | [Introduccion y recorrido](getting-started/) |
| English | [English docs](../getting-started/) |

## Jerarquia de recursos

El modelo mental principal de Moonin es jerarquico. La mayoria de las pantallas, filtros y permisos siguen esta cadena:

```mermaid
flowchart TD
    O[Organizacion]
    P[Proyecto]
    C[Cluster]
    N[Namespace]
    D[Deployment o Service]
    R[Revision]
    E[Error]
    CJ[CronJob]

    O --> P
    P --> C
    C --> N
    N --> D
    D --> R
    R --> E
    N --> CJ
```

## Que significa cada nivel

- `Organizacion` es el limite de tenant para usuarios, grupos, billing, canales, politicas y SSO.
- `Proyecto` agrupa clusters que pertenecen al mismo dominio de negocio, equipo o entorno.
- `Cluster` es el objetivo Kubernetes registrado y conectado por el agente de Moonin.
- `Namespace` delimita workloads dentro del cluster.
- `Deployment` es la unidad de cambio que Moonin correlaciona con revisiones y errores.
- `Service` es la vista orientada a trafico y observabilidad del workload.
- `Revision` es el snapshot inmutable creado por un rollout.
- `CronJob` es la unidad de ejecucion programada, separada del historial de revisiones.

## Flujos nucleares del producto

### 1. Dar de alta y descubrir

```mermaid
flowchart LR
    A[Consola Admin]
    B[Crear organizacion]
    C[Crear proyecto]
    D[Registrar cluster]
    E[Instalar agente Moonin]
    F[Sincronizar inventario]

    A --> B --> C --> D --> E --> F
```

### 2. Seguir un rollout

```mermaid
flowchart LR
    A[Cambio en deployment]
    B[Se crea revision]
    C[Se adjuntan imagenes y servicios]
    D[Se adjunta contexto cloud y HPA]
    E[La release queda visible]

    A --> B --> C --> D --> E
```

### 3. Investigar un incidente

```mermaid
flowchart LR
    A[Falla de pod o job]
    B[Moonin registra error]
    C[Error vinculado a revision y workload]
    D[Se evaluan politicas]
    E[Operador abre Errors o History]
    F[Mitiga o reconoce]

    A --> B --> C --> D --> E --> F
```

### 4. Notificar al canal correcto

```mermaid
flowchart LR
    A[Canales de la organizacion]
    B[Politica de alerta o evento]
    C[Hace match alcance y tiempo]
    D[Se valida ventana UTC y estado enabled]
    E[Entrega por Slack, Teams o VictorOps]

    A --> B --> C --> D --> E
```

## Modelo de acceso resumido

Moonin combina membresia base con roles finos:

- `organization.owner` tiene control total de la organizacion.
- Las membresias base son `viewer`, `editor` y `admin`.
- `viewer` es el rol minimo y sigue minimo privilegio por defecto.
- Por defecto `viewer` puede listar organizaciones y depende de permisos asignados por un admin para obtener acceso adicional.
- Los roles directos a usuario pueden agregar permisos especificos por funcionalidad.
- Los roles heredados por grupo permiten compartir acceso sin editar usuario por usuario.
- Algunas pantallas ademas exigen permisos puntuales como ver revisiones, revisar RCA, editar politicas o administrar clusters.

El modelo completo esta documentado en [Administracion](administration/index.md) y [Azure AD](integrations/azure-ad.md).

## Mapa de documentacion

| Necesidad | Pagina |
|---|---|
| Entender releases, revisiones y contexto de rollout | [Revisiones](revisions/index.md) |
| Operar deployments e inventario de imagenes | [Deployments e imagenes](deployments/index.md) |
| Operar clusters y nodos | [Clusters y nodos](clusters/index.md) |
| Entender servicios, CronJobs e historial de ejecuciones | [Workloads, servicios y CronJobs](workloads/index.md) |
| Investigar fallas activas e historicas | [Errores e incidentes](incidents/index.md) |
| Configurar canales y entender la entrega | [Notificaciones](notifications/index.md) |
| Configurar alertas, eventos y automatizacion de scaling | [Politicas y gobernanza](policies/index.md) |
| Gestionar organizaciones, proyectos, usuarios, grupos y clusters | [Administracion](administration/index.md) |
| Configurar Microsoft Entra ID por organizacion | [Azure AD](integrations/azure-ad.md) |
