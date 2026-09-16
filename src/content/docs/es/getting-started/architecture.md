---
title: "Arquitectura"
---

Este documento describe la arquitectura de alto nivel de Moonin con foco en los componentes visibles hoy en el producto y en el flujo publico de despliegue.

## Resumen

Moonin es una plataforma SaaS multi-tenant desplegada sobre Kubernetes. Los clientes instalan el chart `moonin-agent` dentro de sus clusters. Ese chart hoy incluye el Discovery Agent y el Scaling Rules Agent, ambos autenticados con el mismo secreto de credenciales.

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

## Componentes principales

### Discovery Agent

- observa Deployments, Jobs, CronJobs, HPAs, Namespaces y Services
- envia metadata de deployment, snapshots de nodos, CronJobs y cloud metadata
- usa leader election

### Scaling Rules Agent

- aplica cambios temporales de HPA
- guarda estado de rollback
- restaura los valores anteriores al vencer o deshabilitar la regla

### API de control

Centraliza seguimiento de deployments, clusters, CronJobs, politicas, administracion y billing.

### Aplicacion principal

Entrega:

- overview
- clusters, nodos y namespaces
- deployments, revisiones e imagenes
- CronJobs y ejecuciones
- errores, notificaciones y politicas

### Consola de administracion

Administra:

- organizaciones y usuarios
- proyectos y registro de clusters
- canales de notificacion
- billing

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
