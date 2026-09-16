---
title: "Workloads, servicios y CronJobs"
---

Esta página documenta las vistas runtime que más se usan después del onboarding del cluster:

- `https://app.moonin.app/services`
- `https://app.moonin.app/images`
- `https://app.moonin.app/cronjobs`

Complementa la vista orientada a cambios documentada en [Deployments e imagenes](../deployments/).

## Modelo de navegación de workloads

Moonin expone el mismo estate runtime a traves de lentes operacionales diferentes:

- `Deployments` está centrado en rollouts y revisiones
- `Services` está centrado en trafico, logs, dependencias y observabilidad
- `Images` está centrado en blast radius de imagenes
- `CronJobs` está centrado en comportamiento de ejecución programada

## Página de services

La página `Services` es el punto de entrada para operaciones centradas en el servicio. Agrupa servicios por:

- proyecto
- cluster
- namespace
- nombre de servicio o deployment

El listado sirve para encontrar el workload y luego entrar a una vista de detalle orientada al servicio.

## Vista Service 360

Cuando abres un servicio específico, Moonin organiza la investigación en pestanas:

- `Overview`
- `Logs`
- `Patterns`
- `Events`
- `Metrics`
- `Dependencies`
- `Used By`

En terminos operativos, cada pestana responde preguntas distintas:

- `Overview` resume logs recientes, errores, actividad HTTP y recursos salientes
- `Logs` se enfoca en evidencia runtime actual
- `Patterns` ayuda a identificar comportamiento repetido
- `Events` muestra cambios operativos a nivel evento
- `Metrics` muestra el estado de performance del servicio
- `Dependencies` muestra recursos downstream usados por el servicio
- `Used By` muestra dependencias inversas y consumidores

El detalle de service devuelve la investigación profunda de revisiones y errores a sus vistas especializadas, porque esos flujos tienen mejor contexto de cambio.

## Página de imagenes

La pantalla `Images` es compartida con operaciones de deployment, pero muchas veces se usa desde una mirada de servicio o seguridad:

- identificar todos los servicios que usan una imagen
- comparar tags entre namespaces o clusters
- confirmar cuan extendido esta un build riesgoso
- ubicar la revisión y el deployment exactos detras de una imagen

## Página de CronJobs

Los CronJobs son workloads programados de primera clase en Moonin, no solo un efecto colateral de la captura de eventos generales.

Para cada CronJob, Moonin rastrea:

- expresión cron
- interpretación humana del horario
- timezone configurada
- estado suspendido
- política de concurrencia
- último schedule
- último exito
- cantidad de jobs activos
- último estado de ejecución
- total de ejecuciones
- total de ejecuciones fallidas

## Historial de ejecuciones de CronJob

Cada ejecución puede incluir:

- nombre del Job y job UID
- pod name cuando existe
- estado de la ejecución
- timestamps de inicio y termino
- duración
- exit code
- failure reason
- failure message
- failure logs cuando existen

## Como se capturan las fallas de ejecución de CronJob

```mermaid
flowchart LR
    A[Update de Job]
    B[Moonin resuelve el CronJob owner]
    C[Se deriva el estado de la ejecución]
    D[Se extraen reason y exit code]
    E[Se intentan traer logs del pod relevante]
    F[La ejecución se guarda en Moonin]

    A --> B --> C --> D --> E --> F
```

En la práctica:

- solo los jobs que realmente pertenecen a un CronJob se tratan como ejecuciones de CronJob
- para ejecuciones fallidas, Moonin intenta ubicar el pod y contenedor más relevantes
- si hay logs disponibles, se adjuntan para triage rápido dentro de Moonin

## Que cuenta como falla de CronJob

Moonin trata una ejecución como fallida cuando el estado del job y del contenedor muestra condiciones de error, incluyendo razones comunes como:

- exit code distinto de cero
- `Error`
- `OOMKilled`
- `DeadlineExceeded`

## Como elegir la página correcta

Usa `Services` cuando tu pregunta es sobre comportamiento vivo:

- quien depende de este servicio
- que esta logueando
- cuanta actividad tiene ahora

Usa `CronJobs` cuando tu pregunta es sobre automatización programada:

- si corrio
- si termino
- que fallo

Usa `Images` cuando tu pregunta es sobre huella de despliegue:

- donde está corriendo este contenedor
- que workloads siguen usando este tag

Usa `Deployments` o `Releases` cuando tu pregunta es sobre historial de cambios:

- que cambio
- cuando cambio
- que revisión introdujo el problema
