---
title: "Politicas y gobernanza"
---

La gobernanza en Moonin se construye sobre tres familias de politicas operativas:

- alert policies
- event notification policies
- scaling rules

Esta pagina documenta el comportamiento detras de:

- `https://app.moonin.app/alert-policies`
- `https://app.moonin.app/event-notification-policies`
- `https://app.moonin.app/scaling-rules`

## Jerarquia de politicas

Las tres familias heredan el limite de organizacion y luego acotan el alcance mediante path y contexto del workload.

```mermaid
flowchart TD
    O[Organizacion]
    S[Filtros de alcance]
    C[Canales o acciones]
    R[Resultado runtime]

    O --> S --> C --> R
```

## Alert policies

Las alert policies son guiadas por errores. Evalúan errores capturados de revisiones de deployment y deciden si debe enviarse una notificacion.

### Inputs de una alert policy

Una alert policy puede combinar:

- nombre y descripcion
- estado enabled
- uno o mas tipos de error
- affected ratio minimo
- matching por path
- alcance por proyecto, cluster, namespace o deployment
- ventana de silencio
- delay en segundos
- uno o mas canales
- ventanas UTC por canal

### Como funciona el matching de alertas

```mermaid
flowchart LR
    A[Se captura error de revision]
    B[Hace match el alcance y path]
    C[Hace match el tipo de error]
    D[Hace match el ratio afectado]
    E[Ya paso el delay]
    F[La politica no esta silenciada]
    G[El canal esta en ventana activa]
    H[Se envia la alerta]

    A --> B --> C --> D --> E --> F --> G --> H
```

### Que significa el delay

El delay evita alertar de inmediato ante fallas demasiado frescas. Moonin espera a que transcurra la cantidad de segundos configurada desde la ocurrencia del error antes de enviar.

Usa delay cuando:

- el error suele ser transitorio durante startup
- quieres reducir ruido por turbulencia corta durante el rollout

### Que significa el affected ratio

El affected ratio refleja que tanto del workload esta impactado. Esto permite distinguir:

- un pod inestable dentro de un rollout mas grande
- una falla amplia que afecta a la mayor parte del servicio

## Event notification policies

Las event notification policies no dependen de errores. Sirven para enrutar eventos de ciclo de vida al canal correcto.

### Inputs de una event policy

Una event policy puede combinar:

- nombre y descripcion
- estado enabled
- tipos de evento
- matching por path
- ventana de silencio
- uno o mas canales
- ventanas UTC por canal

### Modelo de eventos actual

El flujo documentado actual incluye:

- `deployment.revision.created`

Eso hace que las event policies sean utiles cuando el equipo quiere enterarse de un despliegue incluso antes de que exista un incidente.

### Flujo de evaluacion de eventos

```mermaid
flowchart LR
    A[Se crea revision]
    B[La event policy hace match por path]
    C[Hace match el tipo de evento]
    D[La politica no esta silenciada]
    E[El canal esta activo ahora]
    F[Se envia la notificacion]

    A --> B --> C --> D --> E --> F
```

## Scaling rules

Las scaling rules son acciones runtime programadas o manuales diseñadas para sobreescribir temporalmente el comportamiento de escalado de un servicio de forma controlada y auditable.

### Que contiene una scaling rule

- nombre
- descripcion
- cron expression
- timezone
- duracion opcional en minutos
- fecha opcional de expiracion
- estado enabled
- informacion del creador
- una o mas acciones de scaling asociadas a deployments

### Que contiene una accion de scaling

Para cada deployment seleccionado, Moonin puede guardar:

- proyecto
- cluster
- namespace
- deployment
- replicas minimas
- replicas maximas
- replicas por defecto
- contexto HPA cuando existe

### Flujo de scaling rules

```mermaid
flowchart LR
    A[Crear template de regla]
    B[Adjuntar acciones por deployment]
    C[La regla queda elegible por horario]
    D[Corre una ejecucion manual o programada]
    E[Se aplica la ventana temporal de scaling]
    F[Se registran eventos y auditoria]

    A --> B --> C --> D --> E --> F
```

### Comportamiento de duracion y expiracion

- `duration_minutes` controla cuanto tiempo permanece activa una ejecucion
- `valid_until` define la ultima fecha en que la regla se considera valida
- una regla puede ejecutarse por horario o manualmente
- la ejecucion manual puede crearse y cancelarse por separado del template

### Para que suelen usarse

- preparar picos de trafico
- bajar capacidad despues de una ventana conocida
- coordinar scaling temporal durante mantenimiento o releases
- documentar que deployments se estan escalando intencionalmente y cuanto

### Auditabilidad

Las scaling rules incluyen vistas de apoyo para:

- revision de acciones
- historial de eventos
- historial de auditoria
- estado de ejecuciones manuales

Toma esas pantallas como la fuente operativa de verdad para el scaling temporal planificado.

## Como elegir la familia correcta

Usa `Alert Policies` cuando el disparador es una falla.

Usa `Event Notification Policies` cuando el disparador es un evento operativo, por ejemplo una nueva revision.

Usa `Scaling Rules` cuando el resultado deseado es un cambio temporal de scaling y no una notificacion.
