---
title: "Primer recorrido"
---

Este recorrido asume que el cluster ya esta registrado y el chart instalado.

## Tour rápido

### 1. Confirmar heartbeat

En **Clusters** valida:

- estado saludable
- metadata de provider
- namespaces y deployments visibles

### 2. Abrir overview

En **Overview** revisa:

- clusters monitoreados
- imagenes detectadas
- CronJobs y ejecuciones recientes
- errores y señales de falla

### 3. Revisar nodos

En **Nodes** valida:

- readiness
- CPU y memoria capacidad vs asignable
- instance type, zona y runtime
- timestamp de captura

### 4. Revisar revisiones e imagenes

Desde **Deployments**:

- abre un servicio
- mira la última revisión
- valida imagenes y tags
- revisa metadata de Helm si existe

### 5. Validar CronJobs

En **CronJobs** veras:

- cron raw
- horario legible
- alcance por namespace y cluster
- ejecuciones recientes
- logs de falla cuando corresponde

### 6. Configurar las policies de respuesta

Crear o actualizar:

- **Alert Policies** para las señales de error
- **Event Notification Policies** para eventos de despliegue o de plataforma

Los canales de notificación se crean en la **Consola de administración** y después se
eligen desde la aplicación principal.
