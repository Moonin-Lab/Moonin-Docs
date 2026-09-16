---
title: "FAQ"
---

## ¿El chart instala más de un agente?
Si. El chart `moonin-agent` actual incluye Discovery Agent y Scaling Rules Agent.

## ¿Los valores de Nodes son como `kubectl top`?
No. La página Nodes muestra snapshots de inventario basados en capacidad y asignable, no consumo vivo.

## ¿Moonin puede mostrar fallas de CronJobs?
Si. Moonin rastrea CronJobs, ejecuciones de Jobs y guarda hasta las últimas 200 líneas de logs de ejecuciones fallidas.

## ¿Qué pasa si se deshabilita una scaling rule?
El Scaling Rules Agent debe hacer rollback al baseline anterior del HPA, igual que cuando la regla expira por tiempo.

## ¿Dónde se crean los notification channels?
En la Consola de administración, dentro de la organización.

## ¿Moonin conserva los nombres de los Secrets en los manifiestos sanitizados?
Si. Los valores sensibles se ocultan, pero la identidad de los recursos —como el
nombre de un Secret— se conserva para dar contexto al diagnostico.
