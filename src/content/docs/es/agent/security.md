---
title: "Modelo de seguridad"
---

Moonin esta disenado para que el bundle del cluster se mantenga acotado, auditable y separado de las credenciales de las aplicaciones de usuario.

## Credenciales del cluster

- El chart guarda `PROJECT_ID`, `CLUSTER_ID` y `CLUSTER_TOKEN` en un Secret compartido.
- Todos los agentes del bundle reutilizan ese Secret.
- Las credenciales autentican al cluster frente a Moonin. No son credenciales de sesion del browser.
- Los cluster tokens pueden rotarse sin re-registrar el objeto cluster.

## Transporte y limite de confianza

- La comunicacion agente-plataforma usa HTTPS.
- Las aplicaciones de usuario proxyean sus requests server-side y no exponen credenciales internas del cluster al browser.
- El cluster autentica como cluster. Los usuarios autentican por separado en las aplicaciones de Moonin.

## Sanitizacion de datos de Discovery

Cuando el Discovery Agent deriva contexto de revision desde releases de Helm o manifests:

- los valores sensibles se redaccionan antes de almacenar
- las identidades de recursos permanecen visibles
- el contexto de troubleshooting se conserva sin guardar payloads secretos

Eso permite que Moonin siga mostrando nombres de Secrets, ConfigMaps, workloads y namespaces sin almacenar contenido sensible.

## Ownership de scaling y seguridad del rollback

El Scaling Rules Agent protege el ownership del HPA de varias formas:

- anota los HPAs administrados con ownership de template y accion
- guarda el spec original del HPA antes de sobrescribir un HPA existente
- guarda la cantidad original de replicas del Deployment antes de cambiar el baseline de ejecucion
- rechaza tomar control de un HPA administrado por otro template o accion activa

Estos controles son los que hacen que el scaling programado sea reversible y no solo imperativo.

## Limites de mutacion

- El Discovery Agent no muta workloads.
- El Scaling Rules Agent solo muta Deployments y HPAs involucrados en un scaling template activo.
- Si el Scaling Rules Agent crea un HPA solo para la ventana de ejecucion, ese HPA se elimina durante el revert despues de restaurar el baseline original del Deployment.

## Lo que el bundle no hace

- No expone credenciales del cluster a usuarios finales.
- No almacena valores completos de secretos en la plataforma.
- No actua como proxy generico de trafico ni como shell privilegiada del cluster.
