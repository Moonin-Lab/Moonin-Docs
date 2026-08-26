# Protocolos de comunicacion

Los agentes actuales de Moonin se comunican con el control plane por HTTPS usando credenciales acotadas al cluster.

## Credenciales y headers

Ambos agentes reciben estos valores desde el Secret compartido creado por el chart:

- `PROJECT_ID`
- `CLUSTER_ID`
- `CLUSTER_TOKEN`

El cluster token se envia en los requests agente-a-plataforma a traves del header `X-Cluster-Token`. Algunas llamadas internas del Discovery Agent tambien incluyen un bearer header por compatibilidad, pero el modelo de confianza sigue siendo cluster-scoped, no user-scoped.

## Destinos principales

| Flujo | Destino | Usado por | Objetivo |
|---|---|---|---|
| Sync de inventario | `api-discover.moonin.app` | Discovery Agent | namespaces, Deployments, revisiones, errores, imagenes, HPAs, CronJobs y nodos |
| Heartbeat del cluster | `api-discover.moonin.app` | Discovery Agent | disponibilidad del cluster y cloud metadata |
| Polling de templates | `api-scaling-rules.moonin.app` | Scaling Rules Agent | listar templates del cluster |
| Polling de acciones | `api-scaling-rules.moonin.app` | Scaling Rules Agent | cargar acciones para un template activo |
| Eventos de ejecucion | `api-scaling-rules.moonin.app` | Scaling Rules Agent | notificar apply y revert |

## Modelo de requests del Discovery Agent

El Discovery Agent usa dos patrones de comunicacion:

- **Sincronizacion inicial** para namespaces, Deployments y CronJobs cuando parte el lider.
- **Envios en estado estable** disparados por informers y loops periodicos.

Flujo de alto nivel:

1. Leer recursos desde la API de Kubernetes.
2. Normalizar y sanitizar el payload cuando corresponde.
3. Enviar por lotes cuando aplica.
4. Publicar el resultado a la Discovery API usando autenticacion del cluster.

## Modelo de requests del Scaling Rules Agent

El Scaling Rules Agent corre un reconcile fijo cada 30 segundos:

1. Hace `GET` de los templates disponibles para el cluster.
2. Evalua cuales deben correr ahora.
3. Hace `GET` de las acciones para cada template activo.
4. Aplica cambios de HPA en el cluster.
5. Hace `POST` de eventos de ejecucion o rollback hacia la Scaling Rules API.

## Protocolo de evaluacion de templates

La plataforma entrega la metadata del template y el agente evalua:

- si el template esta habilitado
- si la hora actual sigue antes de `valid_until`
- si una ejecucion manual esta marcada como `running`
- si la hora actual cae dentro de la ventana programada en la timezone configurada

Eso significa que el control plane define el template, mientras que el agente del cluster toma la decision final de "corre ahora o no" para ese cluster y ese momento.

## Lookups de cloud metadata

Antes de enviar metadata del cluster, el Discovery Agent puede consultar endpoints de metadata del cloud o derivar contexto desde labels de nodos. Esto ayuda a clasificar el cluster como GKE, EKS, AKS o un entorno desconocido u on-prem.

## Limite entre browser y API

Los usuarios no llaman directamente a las APIs orientadas al cluster desde el browser. `app.moonin.app` y `app-admin.moonin.app` quedan detras de limites server-side y aplican el scope del usuario ahi, mientras los agentes autentican como clusters.
