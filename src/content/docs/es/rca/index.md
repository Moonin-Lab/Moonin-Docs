---
title: "Análisis de causa raiz"
---

Moonin RCA combina historial de deployments, contexto runtime y señales de políticas para acortar el camino desde el sintoma hasta la causa probable.

## Entradas usadas por RCA

- revisiones e imágenes
- alcance por cluster y namespace
- incidentes recientes
- contexto de nodos y workloads
- historial de ejecuciones de CronJobs cuando aplica

## Preguntas útiles para el operador

- ¿el problema empezo después de un rollout?
- ¿hay un job programado que fallo y esté contribuyendo al incidente?
- ¿el problema está acotado a un cluster o es más amplio?
- ¿una scaling rule temporal cambio la capacidad poco antes del incidente?
## Flujo recomendado

1. partir del error activo o del workload
2. revisar la última revisión y la actividad reciente de CronJobs
3. revisar el contexto de cluster y de nodos
4. confirmar si una policy, un silencio o una acción de scaling cambio el camino de
   la respuesta
