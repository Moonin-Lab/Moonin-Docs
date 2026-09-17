---
title: "Recolección de datos"
---

Esta página explica que leen del cluster los agentes actuales de Moonin, que envian a la plataforma y que estado de ejecución mantienen solo el tiempo necesario para completar una reconciliación.

## Datos del Discovery Agent

### Inventario de Deployments y revisiones

Para cada Deployment seguido, Moonin puede recolectar:

- nombre del deployment y namespace
- replicas deseadas, actuales y disponibles
- estrategia de rollout
- labels y annotations
- imágenes de contenedor y tags
- relación con services
- número y tipo de revisión
- timestamps asociados al cambio detectado

Cuando el workload está gestionado por Helm, el agente también deriva:

- nombre del release
- nombre y versión del chart cuando están disponibles
- número de revisión Helm
- contexto sanitizado derivado del manifest para revisar la revisión

### Ciclo de vida de pods y señales de error

El Discovery Agent observa pods para reportar señales que ayudan a construir la vista de Errors y Revisión, incluyendo:

- cambios en restart count
- `CrashLoopBackOff`
- `OOMKilled`
- fallas de readiness de contenedores
- cambios de fase como `Pending`, `Running`, `Succeeded` y `Failed`

### Snapshots de HPA

Moonin guarda contexto del HPA asociado a los Deployments, incluyendo:

- replicas minimas
- replicas maximas
- métricas objetivo
- behavior
- estado capturado al momento del sync

### Namespaces, services y topologia

El agente también descubre:

- nombres, labels y annotations de namespaces
- nombres de services, selectors, tipos y puertos
- inventario de ingresses y network policies
- metadata de algunos objetos RBAC para contexto topologico

### Definiciones de CronJobs

Para cada CronJob seguido, el agente envia:

- nombre del CronJob
- namespace
- expresión cron cruda
- timezone si existe
- política de concurrencia
- flag de suspendido
- último schedule
- último exito
- cantidad de jobs activos

### Historial de ejecución de CronJobs

Para cada Job hijo de un CronJob seguido, Moonin puede guardar:

- nombre y UID del Job
- estado de ejecución
- hora de inicio
- hora de termino
- duración
- nombre del pod asociado a la falla
- motivo de falla
- mensaje de falla
- exit code
- hasta las últimas 200 líneas de logs para ejecuciones fallidas

### Metadata de nodos y del cluster

Los snapshots de nodos incluyen periodicamente:

- nombre del nodo
- capacidad y asignable de CPU, memoria, storage y pods
- condiciones como `Ready`, `MemoryPressure` y `DiskPressure`
- runtime, OS image, arquitectura e instance type
- región y zona cuando se pueden derivar

Los heartbeats de metadata del cluster pueden incluir:

- versión de Kubernetes
- cloud provider
- nombre e identificador del cluster cuando se pueden derivar
- región y zona
- número de nodos
- estado de conectividad

!!! note
    La vista de Nodes muestra snapshots de inventario, no uso vivo de recursos estilo `kubectl top`.

## Estado y evidencia del Scaling Rules Agent

El Scaling Rules Agent no es un colector de inventario, pero si deriva y transmite estado de ejecución.

### Datos que lee durante apply

Para aplicar una acción, el agente lee:

- nombre y namespace del Deployment objetivo desde la acción del template
- cantidad actual de replicas del Deployment
- HPA actual que apunta a ese Deployment, si existe
- ventana activa del template, timezone, duración y estado de habilitación desde Moonin

### Datos que persiste temporalmente en HPAs administrados

Para que el rollback sea determinista, el agente guarda annotations en el HPA, incluyendo:

- id del template e id de la acción
- nombre del template
- `run_until` de la ejecución
- `priority_up` y `priority_down`
- si el HPA es provisional
- spec original del HPA cuando el HPA existia antes de Moonin
- replicas originales del Deployment
- min y max originales cuando aplica

### Eventos que envia de vuelta a Moonin

Después de aplicar o revertir, el agente pública evidencia de ejecución como:

- id de la acción
- deployment y namespace
- valores min y max pedidos por la acción
- `run_until` efectivo
- si el HPA era provisional
- razon del revert, por ejemplo `expired` o `disabled`

## Modelo de recolección

El bundle combina dos patrones:

- recolección casi en tiempo real basada en informers para Discovery Agent
- polling periódico y reconciliación para Scaling Rules Agent

Esto es intencional. Discovery sigue eventos del cluster, mientras scaling sigue el estado de templates definido en el control plane.

## Filtros y reducción de alcance

El chart expone configuración para reducir lo que Discovery recolecta:

| Opción | Efecto |
|---|---|
| `ignore_namespaces` | Excluye namespaces completos del discovery |
| `ignore_resources` | Excluye recursos que coincidan con globs |
| `ignore_node_labels` | Evita enviar ciertos labels de nodos |

```yaml
log_level: info
ignore_namespaces:
  - kube-system
ignore_resources:
  - job/*
ignore_node_labels:
  - beta.kubernetes.io/arch
```

## Lo que no se almacena localmente

- Los agentes no mantienen una base de datos local persistente.
- Discovery mantiene estado en memoria y reconcilia continuamente con la plataforma.
- El contexto de rollback de scaling viaja en annotations del HPA administrado, no en un store local aparte.
