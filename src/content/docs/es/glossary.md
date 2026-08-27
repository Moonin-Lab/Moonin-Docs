---
title: "Glosario"
---

**Organizacion**
: Cuenta principal de Moonin que contiene usuarios, proyectos, clusters y canales de notificacion.

**Proyecto**
: Agrupacion logica usada para ordenar clusters y workloads.

**Cluster**
: Cluster Kubernetes registrado en Moonin y autenticado con un cluster token.

**Discovery Agent**
: Componente in-cluster que descubre recursos, envia revisiones, snapshots de nodos, metadata del cluster e historial de CronJobs.

**Scaling Rules Agent**
: Componente in-cluster que aplica cambios temporales de HPA y restaura el estado previo cuando la regla vence o se deshabilita.

**Revision**
: Checkpoint inmutable de rollout para un deployment.

**Ejecucion de CronJob**
: Corrida de un Job hijo de un CronJob, capturada por Moonin con estado, tiempos y logs de falla opcionales.

**Notification channel**
: Destino de entrega administrado por la organizacion, como Slack o Teams.

**Alert policy**
: Regla que evalua fallas operativas y las enruta a canales.

**Event notification policy**
: Regla que enruta eventos de plataforma o deployment a canales.

**Rollback state**
: Baseline de HPA guardado para revertir cambios temporales de scaling.
