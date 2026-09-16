---
title: "Empezar aqui"
---

Esta seccion es la ruta mas rapida para dejar Moonin utilizable. Cubre onboarding del cluster, instalacion por Helm, las primeras vistas que conviene abrir y como esta organizado el producto hoy.

## Orden recomendado

1. [Resumen del producto](overview/)
2. [Instalacion](installation/)
3. [Primer recorrido](quickstart/)
4. [Arquitectura](architecture/)

## Que quedara listo al final

- un proyecto y cluster registrados desde la Consola de administracion
- el chart `moonin-agent` instalado con el secreto compartido de credenciales
- heartbeats del Discovery Agent reportando cluster, namespaces, deployments, CronJobs y nodos
- el Scaling Rules Agent habilitado si lo deseas
- acceso a overview, errores, revisiones, clusters, nodos, imagenes y CronJobs

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
