# Arquitectura

Este documento describe la arquitectura de alto nivel de Moonin con foco en los componentes visibles hoy en el producto y en el flujo publico de despliegue.

## Resumen

Moonin es una plataforma SaaS multi-tenant desplegada sobre Kubernetes. Los clientes instalan el chart `moonin-agent` dentro de sus clusters. Ese chart hoy incluye el Discovery Agent y el Scaling Rules Agent, ambos autenticados con el mismo secreto de credenciales.

## Componentes principales

### Discovery Agent

- observa Deployments, Jobs, CronJobs, HPAs, Namespaces y Services
- envia metadata de deployment, snapshots de nodos, CronJobs y cloud metadata
- usa leader election

### Scaling Rules Agent

- aplica cambios temporales de HPA
- guarda estado de rollback
- restaura los valores anteriores al vencer o deshabilitar la regla

### API de control

Centraliza seguimiento de deployments, clusters, CronJobs, politicas, administracion y billing.

### Aplicacion principal

Entrega:

- overview
- clusters, nodos y namespaces
- deployments, revisiones e imagenes
- CronJobs y ejecuciones
- errores, notificaciones y politicas

### Consola de administracion

Administra:

- organizaciones y usuarios
- proyectos y registro de clusters
- canales de notificacion
- billing
