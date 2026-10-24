---
title: "Operaciones y diagnóstico"
description: "Valide, mantenga, repare, actualice y retire Enterprise con seguridad y sin exponer credenciales."
sidebar:
  order: 6
---

Use estos procedimientos tras la [instalación](../installation/). Reconfirme contexto Kubernetes y ventana aprobada antes de escribir. Las consultas no sustituyen aceptación extremo a extremo y una release saludable no demuestra recuperación de bases ni capacidad suficiente.

## Aceptación y salud continua

Empiece por estado de solo lectura del Installer y Kubernetes. Adapte namespaces y nombres ClickHouse personalizados. Con ClickHouse externo use verificaciones aprobadas del proveedor, no estado interno. `migrate status` exige conexión segura accesible desde la estación.

```bash
kubectl config current-context
moonin-installer platform status
moonin-installer clickhouse status
moonin-installer migrate status
kubectl -n moonin get pods,deployments,statefulsets,services,ingress,pvc
kubectl -n nats get pods,statefulsets,pvc
kubectl -n moonin-clickhouse get pods,services,pvc
kubectl get nodes
kubectl -n moonin get events --sort-by=.metadata.creationTimestamp
```

Revise eventos localmente antes de compartir: elimine nombres y mensajes potencialmente sensibles. No vuelque Secrets ni kubeconfig sin filtrar para diagnóstico. Descubra nombres reales de workloads, sin suponerlos iguales entre versiones del chart.

| Área de aceptación | Evidencia necesaria |
| --- | --- |
| Workloads y almacenamiento | Réplicas Ready esperadas, sin reinicios repetidos, PVC Bound, zonas/selectores correctos, sin errores de scheduling o adjuntar volumen |
| DNS/HTTPS | Hosts reales Portal/Admin resuelven al ingress aprobado y presentan certificados confiables coincidentes |
| Autenticación | Login/logout independientes, acceso propietario, límites organizativos, proveedores activos, verificación email y MFA cuando aplique |
| Invitaciones | Destinatario no demo aprobado recibe invitación y completa primer login/contraseña/MFA |
| Base y analytics | Estado de migraciones aplicado, API conecta en runtime, consultas analytics exitosas, sin fallos TLS/privilegios |
| Telemetría | Workload controlado envía datos actuales visibles y consultables en organización/proyecto previstos |
| Capacidad | Tasas y latencia de ingesta/consulta, colas, crecimiento de disco, CPU/memoria y margen para retención medidos |
| Recuperación | Restauración probada PostgreSQL, ClickHouse y JetStream, responsables y objetivos de recuperación |

Platform no instala agentes en todos los clústeres monitorizados. Coordine [onboarding de agentes](../../getting-started/installation/) por separado con endpoints y credenciales Enterprise aprobados, no defaults alojados. Compruebe timestamps recientes y límites de tenant; un dashboard con datos antiguos no demuestra ingesta actual.

Si metrics-server existe y tiene autorización, puede consultar adicionalmente:

```bash
kubectl top nodes
kubectl -n moonin top pods
kubectl -n nats top pods
kubectl -n moonin-clickhouse top pods
```

La ausencia de metrics-server no implica fallo de instalación Moonin. Las instantáneas CPU/memoria no miden disco, ingesta, retención ni salud analytics completa; use también métricas de almacenamiento/cloud y dashboards aprobados. Compare con requests/limits y tráfico esperado, no solo con la recomendación preliminar PoC.

## Renovar o reparar licencia

```bash
moonin-installer license install
```

Pegue el JWS firmado completo interactivamente. Valida firma, vigencia, cliente/tipo y límites antes de aplicar `moonin/moonin-license`, clave `MOONIN_LICENSE`. `license upgrade` es alias. Licencias inválidas, alteradas o caducadas no modifican Kubernetes. Reutiliza namespaces existentes; renovar no requiere desinstalar Platform.

Después programe reinicio/redeploy controlado de consumidores que leen licencia al arrancar y verifique readiness y funcionalidades. Actualizar el Secret no garantiza recarga en procesos vivos. No use borrado de namespace, edición de base ni override de servicios SaaS para reparar validación. Mantenga licencia fuera de evidencias y argumentos.

## Reparar conexiones o autenticación

| Necesidad | Procedimiento soportado | Seguimiento |
| --- | --- | --- |
| Autenticación Portal | `moonin-installer portal configure` | Revise URL/proveedor/cookie y haga rollout controlado de consumidores |
| Autenticación Admin | `moonin-installer platform auth admin configure` | Revise reutilización, secreto/cookie independientes y rol de invitaciones |
| Conexión ClickHouse | `moonin-installer clickhouse connection` | Verifique protocolo nativo/TLS y conectividad runtime; redeploy de consumidores si procede |
| Secret PostgreSQL runtime / prerrequisitos completos | Reejecute `platform install` revisado o etapa Secret runtime del asistente `migrate` | Revise acción de migración cuidadosamente; preserve datos y confirme cuenta/TLS runtime |
| Organización inicial ausente | `moonin-installer bootstrap organization` con `DATABASE_URL` segura | Solo si ninguna existe y hay esquema aplicado; prepare Entra obligatorio |

Los comandos de autenticación no actualizan Helm ni reinician Pods. Los consumidores `envFrom` necesitan Pods nuevos para tomar variables nuevas. Descubra primero workloads con `kubectl -n moonin get deployments,statefulsets`, siga su proceso aprobado de rollout/redeploy para consumidores reales, monitorice readiness y repita pruebas. Rote secretos de sesión solo intencionadamente: invalida sesiones. Cambiar Portal no sincroniza Admin automáticamente.

No repare acceso o esquema con escrituras SQL manuales. Si ya existe organización, use los flujos soportados Admin de organizaciones/usuarios. Repetir bootstrap inicial no recupera cuentas.

## Actualización controlada Platform

1. Registre versión Installer, chart/appVersion actual, imágenes reales, overrides explícitos no sensibles, versiones de dependencias y propiedad.
2. Seleccione chart objetivo publicado real; revise compatibilidad, migraciones y cambios con soporte/gestión de cambios. Valide antes en no producción.
3. Respalde PostgreSQL, ClickHouse y JetStream y verifique restauración. Rollback Helm no restaura datos ni revierte automáticamente migraciones separadas.
4. Planifique migraciones necesarias en orden aprobado. `migrate status` informa estado; no use `down`/`reset` como recuperación genérica.
5. Ejecute actualización del chart con objetivo revisado y, si hace falta, archivo values existente sin secretos.
6. Inspeccione plan y cambios previos NATS antes de aceptar. Repita aceptación completa después.

```bash
moonin-installer platform upgrade --help
moonin-installer platform upgrade \
  --version APPROVED_CHART_VERSION \
  --values /absolute/path/enterprise-values.yaml
moonin-installer platform status
```

Sustituya marcadores u omita `--values` sin overrides. Versiones Installer, chart y aplicación siguen siendo distintas. Cambia el chart; no es autoactualización del comando de estación.

`platform upgrade` no repite todo el asistente de autenticación/Secrets, pero puede pedir cambios NATS confirmados antes de bootstrap. Prioridad ascendente: defaults del nuevo chart, configuración explícita previa, valores generados y `--values`. Las imágenes solo de defaults pueden avanzar mientras pins explícitos permanecen. Revise imágenes resultantes; no suponga actualización uniforme. Reejecute `platform install` cuando necesite revisar prerrequisitos.

El modo atómico Helm cubre su install/upgrade fallido, no cambios anteriores de Secrets/dependencias, migraciones externas ni verificación posterior a Helm exitoso. Comprueba imágenes declaradas renderizadas y plantillas vivas, incluidos init containers; mismatches posteriores impiden éxito sin rollback automático. Inspeccione despliegue real antes de reintentar.

## Placement y reparación NATS

Para NATS `2.14.2`, la ruta válida es `podTemplate.merge.spec.nodeSelector`, no legacy `podTemplate.merge.nodeSelector`. Un selector `spec` válido, incluso vacío, es autoritativo. Compara placement deseado/efectivo con nodos Ready y afinidad de zonas PV; la reparación confirmada elimina ruta legacy preservando otros overrides.

Si placement deseado no cubre todas las zonas PV, recupere nodos compatibles o apruebe explícitamente conservar placement efectivo compatible cuando se ofrezca. Reset no sustituye nodos adecuados. Reparación/reset proponen **No**. Rutas reset legacy pueden perder datos JetStream; guarda valores reparados antes y un fallo Helm no justifica borrar volúmenes. Las releases externas se inspeccionan, no se reparan/resetean por esta ruta consciente de propiedad.

## Retirada controlada y propiedad

Detenga tráfico, acuerde retención, haga backups verificados, inventaríe consumidores/dependencias compartidas y confirme contexto. El ledger `moonin/moonin-platform-install-state` distingue `created`, `reused` y `external`. No lo edite/borre para forzar retirada; sin registro el instalador se niega a adivinar.

```bash
moonin-installer platform uninstall
```

Solo propone retirar recursos propios `created`. Preserva reutilizados/externos y conserva namespaces por defecto. No borra PostgreSQL/RDS ni ClickHouse externo/instalado independientemente. `--yes`, donde existe, omite confirmación, no propiedad; evítelo en la primera retirada revisada.

**Opción destructiva de namespaces:** `platform uninstall --delete-created-namespaces` también puede borrar recursos añadidos después por otros operadores, **incluidos PVC**. No lo use simplemente porque quede un namespace. Inspeccione contenido actual y plan de backup/recuperación antes de aprobar.

Para retirar solo NATS propio conservando normalmente PVC JetStream:

```bash
moonin-installer platform nats uninstall
```

Su flag es singular: `--delete-created-namespace`, también potencialmente destructivo. `platform nats adopt` es solo para recursos legacy verificados como propios del instalador, nunca para apropiarse de una release compartida. Retirar o adoptar no demuestra automáticamente propiedad de datos.

ClickHouse tiene ciclo independiente:

```bash
moonin-installer clickhouse uninstall
```

Confirme namespace/clúster originales con flags compatibles coincidentes si se personalizaron. Retira ClickHouse/Keeper seleccionados y Secret de contraseña **conservando PVC por defecto**. Preserve credenciales de forma segura para recuperar datos retenidos. `--delete-data` elimina permanentemente PVC seleccionados; usa prefijos de nombre del clúster, por lo que debe inspeccionar colisiones antes.

`--remove-operator` y `--remove-cert-manager` son opt-ins independientes. Solo retira dependencias propias registradas que superen comprobaciones de uso compartido; no borra automáticamente namespaces, CRDs o instalaciones preexistentes/compartidos. Retira recursos EKS de ayuda de almacenamiento solo tras verificar PVC, PV EBS y otras asociaciones Pod Identity. Use `--keep-eks-storage` para preservarlos expresamente. Conserva legacy sin registro; `clickhouse adopt-eks-storage` solo corresponde a almacenamiento legacy cuya propiedad del instalador haya verificado independientemente, no elude revisión compartida.

### Rollback de base: acción destructiva separada

`migrate down` revierte la última migración; la acción directa **no** pide la confirmación del asistente. `migrate reset --confirm-reset` revierte todas y puede eliminar objetos de esquema y datos. Confirmaciones interactivas `down`/`reset` proponen **No**, pero eso no hace seguros los comandos directos. No forman parte de retirada normal, reparación de red o reintento habitual. Ejecute solo con plan aprobado por DBA y backups probados.

## Diagnóstico

| Síntoma | Límite probable y siguiente acción |
| --- | --- |
| `exec format error` | Si la estación no inicia el comando, verifique variante SO/CPU de estación. Si lo informa un Pod, revise arquitectura de nodo soportada por esa imagen; Installer multiarch no vuelve multiarch todas las imágenes. No desactive seguridad ni reconstruya dependencias como atajo diagnóstico |
| Kubernetes `Unauthorized` en EKS | Compruebe contexto y renueve sesión AWS/SSO del operador mediante su proceso aprobado; repita consulta de solo lectura. Es distinto de `CrashLoopBackOff`: renovar credenciales del operador no repara un Pod que falla |
| Comando raíz `not implemented` | Use `platform install/status/upgrade/uninstall`, no placeholders raíz similares. `init` solo genera plantilla; no hay `apply -f` o `platform install --config` implementado que la consuma |
| Falta ejecutable/dependencia | Revise `PATH` y versiones `kubectl`, Git, Helm. ClickHouse exige Helm CLI aunque Platform integre Helm |
| Licencia rechazada | Revise JWS completo, vigencia, firma compatible, capacidad declarada y reloj. Obtenga licencia firmada corregida por onboarding; no edite claims |
| Timeout PostgreSQL | Revise DNS privado, VPN/routing, puerto, security groups y red Pod por separado de la estación |
| Error hostname o CA RDS/TLS | Use CA oficial vigente, `verify-full` y DNS coincidente. Revise rutas locales y contenido PEM runtime con herramientas aprobadas; no imprima claves ni desactive verificación para ocultar error |
| Privilegios de migración | Solicite verificar cuenta/base y permisos de objetos/extensiones al DBA; `reset` no repara permisos |
| Falla conexión ClickHouse | Revise endpoint/puerto nativo, esquema seguro, encoding de credenciales, permisos usuario/base, TLS y conectividad runtime |
| Falla sesión Admin / falta `NEXTAUTH_SECRET` | Repare autenticación Admin, asegure secreto independiente, referencia/namespace correctos y prefijo explícito `moonin-admin`; reinicie/repliegue consumidores `envFrom` reales |
| Redirect incorrecto | Compare URL pública, callback/orígenes, DNS, ingress y TLS de ambas aplicaciones |
| Falla MFA/invitación Cognito | Revise enrollment no demo y TOTP del pool; en invitaciones, sujeto/audiencia IRSA exactos, acciones acotadas, anotación ServiceAccount, placeholders y correo |
| PVC Pending / NATS no Ready | Revise CSI, StorageClass, capacidad, nodos Ready, selectores, afinidad PV y zonas. Recupere nodos compatibles antes de resets destructivos |
| ImagePullBackOff | Compruebe imagen/tag, red del registro y referencias pull Secret reales; no invente credenciales |
| Mismatch de imágenes posterior a Helm | Inspeccione workloads y overrides efectivos; el fallo de verificación no revierte automáticamente Helm exitoso |
| Uninstall conserva recursos | Revise propiedad y uso compartido; conservar puede ser lo esperado, no un borrado fallido |

## Evidencia segura y referencia

Aporte versiones Installer/chart/aplicación, SO/arquitectura, etapa, error redactado, readiness y timestamps relevantes. No adjunte DSN con credenciales, JWS, archivos `.env`, kubeconfig sin filtrar, manifiestos Secret, claves privadas, dumps ni logs sin revisar. Use evidencia acotada y redactada en lugar de exportar toda la configuración del clúster.

```bash
moonin-installer platform install --help
moonin-installer platform upgrade --help
moonin-installer platform uninstall --help
moonin-installer portal configure --help
moonin-installer platform auth admin configure --help
moonin-installer migrate --help
moonin-installer bootstrap organization --help
moonin-installer license install --help
moonin-installer clickhouse install --help
moonin-installer clickhouse connection --help
moonin-installer clickhouse uninstall --help
```

`--no-color` es global y solo desactiva estilos ANSI. `--yes` depende del comando; no es modo desatendido global. La ayuda suministrada es referencia de flags para su versión. Vuelva al [índice Enterprise](../) o [autenticación](../authentication/) según el flujo.