---
title: "Primer recorrido"
---

Este recorrido asume que el cluster ya está registrado y que el chart de Helm está
instalado.

## Tour rápido

### 1. Confirmar el heartbeat del cluster

Abre **Clusters** y verifica:

- que el estado sea saludable
- que la metadata del provider esté poblada
- que los namespaces y los deployments empiecen a aparecer

### 2. Abrir el tablero de overview

Usa la pantalla **Overview** para validar:

- los clusters monitoreados
- las imágenes encontradas en el alcance actual
- los CronJobs y sus ejecuciones recientes
- las señales activas de error y de tasa de falla

### 3. Revisar un snapshot de nodo

Ve a **Nodes** y verifica el inventario:

- el readiness del nodo
- capacidad contra asignable, en CPU y memoria
- instance type, zona y runtime
- el timestamp de la captura

Los snapshots de nodos son registros de inventario, no uso en vivo como el de
`kubectl top`.

### 4. Revisar revisiones e imágenes

Desde **Deployments**:

- abre un servicio
- revisa su última revisión
- valida los nombres de imagen y sus tags
- revisa la metadata de Helm si el workload está gestionado por Helm

### 5. Validar CronJobs

Abre **CronJobs** para ver:

- la expresión cron en crudo
- el horario legible
- el alcance por namespace y por cluster
- las ejecuciones recientes
- los logs de falla cuando la ejecución de un Job falla

### 6. Configurar las policies de respuesta

Crear o actualizar:

- **Alert Policies** para las señales de error
- **Event Notification Policies** para eventos de despliegue o de plataforma

Los canales de notificación se crean en la **Consola de administración** y después se
eligen desde la aplicación principal.
