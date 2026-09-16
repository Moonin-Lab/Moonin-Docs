---
title: "Resumen del producto"
---

Moonin combina seguimiento de cambios, inventario de clusters y gobernanza operativa para entornos Kubernetes. La idea central es responder rapido tres preguntas:

1. que cambio
2. que esta afectado ahora
3. que politica o automatizacion deberia actuar despues

## Capacidades principales

### Inteligencia de cambios

- historial de deployments y revisiones
- trazabilidad de imagenes entre clusters
- metadata de Helm cuando aplica
- correlacion entre revisiones y errores

### Inventario de runtime

- conectividad de clusters y cloud metadata
- descubrimiento de namespaces y deployments
- snapshots de nodos con capacidad, asignable y condiciones
- CronJobs, horarios y ejecuciones recientes

### Gobernanza operativa

- politicas de alerta con canales de notificacion
- politicas de notificacion de eventos
- scaling rules con rollback automatico
- silencios y horarios por canal

## Aplicaciones principales

| Aplicacion | Para que sirve |
|---|---|
| `app.moonin.app` | Espacio principal de ingenieria: tableros, workloads, revisiones, errores y policies |
| `app-admin.moonin.app` | Consola de administracion de organizaciones, proyectos, clusters y canales de notificacion |
| `api-discover.moonin.app` | API de control que usan los agentes y las aplicaciones web |
| `api-scaling-rules.moonin.app` | Plano de control de las scaling rules |
| `mcp.moonin.app` | Superficie MCP de solo lectura para herramientas y asistentes de IA |

## Areas de la plataforma que reflejan estos documentos

- tablero de overview con senales compactas de salud e inventario
- pagina dedicada de inventario de nodos, con filas expandibles y adaptables
- pagina de CronJobs con historial de ejecuciones y horarios legibles
- mejores enlaces directos a las consolas de AWS y GCP desde el frontend
- event notification policies y la experiencia de horarios por canal
- chart del agente que empaqueta el Discovery Agent y el Scaling Rules Agent

## Quien usa Moonin

- ingenieria de plataforma que administra entornos multi-cluster
- equipos de SRE que revisan el impacto de un rollout y los incidentes activos
- equipos de DevOps que estandarizan notificaciones y comportamiento de scaling
- equipos de aplicacion que validan imagenes, CronJobs e historial de despliegue
