---
title: "Límites y alcance"
---

Esta página documenta los límites intencionales del bundle público actual de agentes.

## Límites del Discovery Agent

- La vista de Nodes muestra snapshots de capacidad y asignable, no muestreo de uso vivo.
- La detección del provider es best effort y depende de acceso a metadata del cloud o de labels útiles en los nodos.
- El historial de ejecución de CronJobs depende de que los Jobs hijos sigan visibles y no esten excluidos por filtros.
- Los logs de ejecuciones fallidas se guardan solo como un tail de hasta 200 líneas, no como archivos completos de logs del pod.
- Los namespaces y recursos excluidos por reglas de ignore se omiten completamente del discovery y de la historia relacionada.
- Discovery ayuda a explicar el estado runtime en Moonin, pero no es un pipeline completo de observabilidad ni reemplaza herramientas dedicadas de métricas, trazas o retención larga de logs.

## Límites del Scaling Rules Agent

- La implementación actual apunta a Deployments mediante HPAs.
- Las ventanas de scaling dependen del estado del template en Moonin más la evaluación temporal local del agente en cada reconcile.
- Los revert ocurren en el siguiente ciclo de reconcile, por lo que una deshabilitación o expiración no es instantanea al milisegundo.
- Si el Deployment objetivo no tiene HPA, el agente puede crear un HPA provisional administrado para esa ventana de ejecución.
- La calidad del rollback depende del baseline original capturado antes de que Moonin tome control del HPA.
- Cambios externos en el HPA o en replicas después de capturar ese baseline pueden afectar el objetivo final del rollback.
- Solo un contexto de ownership administrado puede controlar un HPA dado al mismo tiempo.

## Límites del bundle

- El bundle no proxya requests de usuarios finales hacia el cluster.
- El bundle no crea un store local persistente.
- La documentación pública explica el comportamiento soportado, no heuristicas comerciales internas de la plataforma completa de Moonin.
