---
title: "Resumen del producto"
---

Moonin combina seguimiento de cambios, inventario de clusters y gobernanza operativa para entornos Kubernetes. La idea central es responder rápido tres preguntas:

1. que cambio
2. que esta afectado ahora
3. que política o automatización debería actuar después

## SaaS y Enterprise

**SaaS** es el servicio alojado por Moonin: Moonin opera la plataforma y su equipo conecta los clústeres monitorizados según su suscripción. Las URL públicas de aplicaciones que figuran más abajo corresponden a ese servicio alojado.

**Enterprise** se ejecuta en el entorno Kubernetes de su organización, que opera infraestructura, seguridad, backups y actualizaciones. Requiere una **licencia comercial de cliente Enterprise firmada**. Contacte a Ventas de Moonin mediante su representante de cuenta o el sitio web oficial para acordar capacidad, funcionalidades, vigencia y soporte y obtener la licencia antes de instalar. Descargar la CLI no concede una licencia Enterprise.

Consulte [despliegue y licenciamiento Enterprise](../../enterprise/) para la comparación, el ciclo de la licencia y la guía de instalación. Enterprise utiliza sus propios endpoints aprobados, no las URL del servicio alojado que aparecen más abajo.

## Capacidades principales

### Inteligencia de cambios

- historial de deployments y revisiones
- trazabilidad de imágenes entre clusters
- metadata de Helm cuando aplica
- correlación entre revisiones y errores

### Inventario de runtime

- conectividad de clusters y cloud metadata
- descubrimiento de namespaces y deployments
- snapshots de nodos con capacidad, asignable y condiciones
- CronJobs, horarios y ejecuciones recientes

### Gobernanza operativa

- políticas de alerta con canales de notificación
- políticas de notificación de eventos
- scaling rules con rollback automático
- silencios y horarios por canal

## Aplicaciones principales

| Aplicación | Para qué sirve |
|---|---|
| `portal.moonin.app` | Espacio principal de ingeniería: tableros, workloads, revisiones, errores y policies |
| `admin.moonin.app` | Consola de administración de organizaciones, proyectos, clusters y canales de notificación |
| `api-discover.moonin.app` | API de control que usan los agentes y las aplicaciones web |
| `api-scaling-rules.moonin.app` | Plano de control de las scaling rules |
| `mcp.moonin.app` | Superficie MCP de solo lectura para herramientas y asistentes de IA |

## Áreas de la plataforma que reflejan estos documentos

- tablero de overview con señales compactas de salud e inventario
- página dedicada de inventario de nodos, con filas expandibles y adaptables
- página de CronJobs con historial de ejecuciones y horarios legibles
- mejores enlaces directos a las consolas de AWS y GCP desde el frontend
- event notification policies y la experiencia de horarios por canal
- chart del agente que empaqueta el Discovery Agent y el Scaling Rules Agent

## Quien usa Moonin

- ingeniería de plataforma que administra entornos multi-cluster
- equipos de SRE que revisan el impacto de un rollout y los incidentes activos
- equipos de DevOps que estandarizan notificaciones y comportamiento de scaling
- equipos de aplicación que validan imágenes, CronJobs e historial de despliegue
