---
title: "Permisos requeridos"
---

El chart publico separa los permisos por agente de forma intencional. Discovery y Node Agent son de solo lectura desde la perspectiva de la API de Kubernetes. Scaling necesita permisos de mutacion para HPAs y para algunos cambios de replicas en Deployments.

## Alcance RBAC del Discovery Agent

El chart actual entrega al Discovery Agent:

- `get`, `list`, `watch` sobre `namespaces`
- `get`, `list`, `watch` sobre `nodes`
- `get`, `list`, `watch` sobre `pods` y `pods/log`
- `get`, `list`, `watch` sobre `services`
- `get`, `list`, `watch` sobre `configmaps`
- `get`, `list`, `watch` sobre `secrets`
- `get`, `list`, `watch` sobre `events`
- `get`, `list`, `watch` sobre `deployments` y `replicasets`
- `get`, `list`, `watch` sobre `horizontalpodautoscalers`
- `get`, `list`, `watch` sobre `jobs` y `cronjobs`
- `get`, `list`, `watch` sobre `ingresses` y `networkpolicies`
- `get`, `list`, `watch` sobre algunos objetos RBAC
- `get`, `list`, `watch`, `create`, `update`, `patch` sobre `leases` para leader election

### Por que existe acceso a `pods/log`

El Discovery Agent lee logs de pods fallidos de Jobs para que Moonin pueda adjuntar contexto de falla al historial de ejecuciones de CronJobs. No archiva logs completos del cluster.

## Alcance RBAC del Scaling Rules Agent

El chart actual entrega al Scaling Rules Agent:

- `get`, `list`, `watch` sobre `pods`
- `get`, `list`, `watch`, `update`, `patch` sobre `deployments`
- `get`, `list`, `watch`, `create`, `update`, `patch`, `delete` sobre `horizontalpodautoscalers`

### Por que necesita mutar Deployments

El Scaling Rules Agent puede subir o restaurar replicas del Deployment mientras aplica o revierte una ventana de scaling basada en HPA. Asi mantiene el workload alineado con el minimo solicitado o con el baseline guardado.

## Alcance RBAC de Node Agent

Node Agent lee contexto de Kubernetes para asociar la telemetria runtime observada desde el host con los workloads. El chart actual le otorga `get` y `list` sobre:

- `pods`, `services` y `endpoints`
- `endpointslices`
- `jobs`
- `replicasets`

Node Agent tambien requiere acceso privilegiado al host para su recoleccion basada en eBPF. Revisa [Node Agent](node-agent.md) para los requisitos completos de acceso al host.

## Limites de permisos

- Discovery no necesita permisos para mutar workloads.
- Node Agent no muta recursos de Kubernetes.
- Scaling no necesita permisos amplios de inventario mas alla de los recursos involucrados en la ejecucion del HPA.
- El chart es la fuente de verdad recomendada para RBAC porque los permisos exactos dependen del comportamiento soportado por la version actual de los agentes.

## Validacion practica despues de instalar

Despues de instalar el chart, valida ambos sets de permisos confirmando que:

- namespaces y Deployments aparezcan en Moonin
- snapshots de nodos y ejecuciones de CronJobs se poblen correctamente
- los scaling templates puedan aplicar y revertir sin errores `Forbidden` sobre HPAs o Deployments
