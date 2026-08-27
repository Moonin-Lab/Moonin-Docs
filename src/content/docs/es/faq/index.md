---
title: "FAQ"
---

## El chart instala mas de un agente?

Si. El chart `moonin-agent` actual incluye Discovery Agent y Scaling Rules Agent.

## Los valores de Nodes son como `kubectl top`?

No. La pagina Nodes muestra snapshots de inventario basados en capacidad y asignable, no consumo vivo.

## Moonin puede mostrar fallas de CronJobs?

Si. Moonin rastrea CronJobs, ejecuciones de Jobs y guarda hasta las ultimas 200 lineas de logs de ejecuciones fallidas.

## Que pasa si se deshabilita una scaling rule?

El Scaling Rules Agent debe hacer rollback al baseline anterior del HPA, igual que cuando la regla expira por tiempo.

## Donde se crean los notification channels?

En la Consola de administracion, dentro de la organizacion.
