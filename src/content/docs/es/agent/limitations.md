---
title: "Limites y alcance"
---

Esta pagina documenta los limites intencionales del bundle publico actual de agentes.

## Limites del Discovery Agent

- La vista de Nodes muestra snapshots de capacidad y asignable, no muestreo de uso vivo.
- La deteccion del provider es best effort y depende de acceso a metadata del cloud o de labels utiles en los nodos.
- El historial de ejecucion de CronJobs depende de que los Jobs hijos sigan visibles y no esten excluidos por filtros.
- Los logs de ejecuciones fallidas se guardan solo como un tail de hasta 200 lineas, no como archivos completos de logs del pod.
- Los namespaces y recursos excluidos por reglas de ignore se omiten completamente del discovery y de la historia relacionada.
- Discovery ayuda a explicar el estado runtime en Moonin, pero no es un pipeline completo de observabilidad ni reemplaza herramientas dedicadas de metricas, trazas o retencion larga de logs.

## Limites del Scaling Rules Agent

- La implementacion actual apunta a Deployments mediante HPAs.
- Las ventanas de scaling dependen del estado del template en Moonin mas la evaluacion temporal local del agente en cada reconcile.
- Los revert ocurren en el siguiente ciclo de reconcile, por lo que una deshabilitacion o expiracion no es instantanea al milisegundo.
- Si el Deployment objetivo no tiene HPA, el agente puede crear un HPA provisional administrado para esa ventana de ejecucion.
- La calidad del rollback depende del baseline original capturado antes de que Moonin tome control del HPA.
- Cambios externos en el HPA o en replicas despues de capturar ese baseline pueden afectar el objetivo final del rollback.
- Solo un contexto de ownership administrado puede controlar un HPA dado al mismo tiempo.

## Limites del bundle

- El bundle no proxya requests de usuarios finales hacia el cluster.
- El bundle no crea un store local persistente.
- La documentacion publica explica el comportamiento soportado, no heuristicas comerciales internas de la plataforma completa de Moonin.
