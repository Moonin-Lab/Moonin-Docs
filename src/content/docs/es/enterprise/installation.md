---
title: "Instalación"
description: "Instale ClickHouse, migre PostgreSQL, cree la primera organización y complete las nueve etapas Platform."
sidebar:
  order: 4
---

Complete primero [requisitos](../requirements/) y [preparación](../preparation/). La CLI pregunta actualmente en inglés. Las etiquetas entre comillas identifican sus prompts; las explicaciones indican qué elegir. Los defaults pueden depender de recursos existentes y de la URL de conexión: lea lo mostrado en lugar de pulsar Enter en todo.

## 1. Confirme el destino

```bash
moonin-installer version
moonin-installer platform install --help
kubectl config current-context
kubectl get nodes
kubectl get storageclass
```

Confirme contexto aprobado, nodos Ready, almacenamiento, conectividad privada de bases de datos, identidad y ventana de mantenimiento. Los ejemplos usan el comando proporcionado por onboarding en `PATH`. Su sintaxis es Bash; adapte a PowerShell. No grabe el terminal ni active trazas del shell al introducir credenciales.

## 2. Prepare ClickHouse antes de migrar

### Opción A: servicio analytics externo

Solicite al DBA base, usuario, endpoint nativo, TLS y acceso de red para consumidores Platform. No ejecute el asistente de instalación. Configure la conexión ahora o en la etapa 5 Platform:

```bash
moonin-installer clickhouse connection
```

El formato URI admite `clickhouse://` para protocolo nativo o `clickhouses://` para conexión nativa segura, con puerto y base del proveedor. Codifique caracteres reservados de credenciales mediante percent-encoding. No use un endpoint HTTP por analogía. Introduzca DSN sensibles interactivamente en terminal protegido; validar sintaxis no demuestra conectividad ni privilegios.

### Opción B: stack inicial dentro del clúster

```bash
moonin-installer clickhouse install
```

Revise cada decisión del asistente antes de iniciar Platform:

| Pregunta o decisión | Valor inicial / acción del operador |
| --- | --- |
| Namespace y nombre del clúster | `moonin-clickhouse` y `clickhouse`; registre cambios para estado/retirada posteriores |
| StorageClass | Propone clase default o elegible `WaitForFirstConsumer`; elija explícitamente CSI durable compatible |
| Volumen de datos ClickHouse | `100Gi`; dimensione según ingesta y retención medidas |
| Volumen Keeper | `10Gi`; incluya recuperación de coordinación en el diseño |
| CPU/memoria | ClickHouse request `1`/`2Gi`, limit `4`/`8Gi`; Keeper request `100m`/`256Mi`, limit `500m`/`512Mi` |
| Selector de nodo | `clave=valor` opcional; vacío deja scheduling a Kubernetes. La etiqueta debe coincidir con nodos Ready y zonas de volúmenes |
| Contraseña | Se reutiliza `clickhouse-password`, clave `password`, si existe; si falta, introduzca y confirme, oculta en terminal compatible |
| Dependencias | Reutilice cert-manager/Operator compatibles, incluso en otros namespaces; revise aprobación antes de crear los ausentes |
| Conexión Platform al finalizar | Se ofrece con default **Sí**; crea el Secret de conexión para Platform |

La topología inicial es una réplica ClickHouse y una Keeper, **no HA**, con timeout `20m`. Si debe instalar cert-manager utiliza `v1.20.4`; el manifiesto Operator sigue `releases/latest`, no una versión fijada. Registre las versiones realmente desplegadas y evalúe compatibilidad Kubernetes antes de producción.

En EKS sin EBS CSI, `"Enable Amazon EBS CSI now through AWS"` (habilitar EBS CSI mediante AWS) propone **Sí**, pero exige aceptación e identidad AWS autorizada. Puede configurar rol dedicado, Pod Identity Agent, EBS CSI y `moonin-ebs-gp3`. Prefiere `AmazonEBSCSIDriverPolicyV2`; advierte si recurre a `AmazonEBSCSIDriverPolicy`, más amplia. Revise alcance IAM antes de aceptar. Las dependencias compartidas se reutilizan, no se asume su propiedad. En GKE/AKS prepare CSI mediante su procedimiento de infraestructura.

Para evitar ambigüedad de detección, estos flags están disponibles:

```bash
moonin-installer clickhouse install \
  --namespace moonin-clickhouse \
  --cluster-name clickhouse \
  --storage-class APPROVED_STORAGE_CLASS \
  --data-size 100Gi \
  --keeper-size 10Gi
moonin-installer clickhouse status
```

Sustituya `APPROVED_STORAGE_CLASS`. Con nombres personalizados, incluya los mismos `--namespace` y `--cluster-name` al consultar estado. No reejecute únicamente para rotar contraseña: se reutiliza el Secret existente.

## 3. Migre la base PostgreSQL dedicada

```bash
moonin-installer migrate
```

El asistente se ejecuta desde la estación, no desde un Pod. No carga automáticamente archivos de entorno. Puede usar `DATABASE_URL` inyectada de forma segura; `--database-url` tiene prioridad, pero no es adecuado para secretos en historial/argumentos de procesos. Nunca apunte a la base de otra aplicación.

| Paso / prompt en inglés | Explicación y default |
| --- | --- |
| 1. `"PostgreSQL connection"` | Conexión PostgreSQL dedicada Moonin. `"Use the supplied database URL"` (usar URL suministrada) propone **Sí** si existe |
| 2. `"PostgreSQL transport security"` / `"TLS mode"` | Seguridad de transporte/modo TLS: revise el derivado de la URL. Prefiera `verify-full`; indique `"CA bundle PEM file path"` (ruta bundle CA) y archivos mTLS opcionales |
| 3. `"Migration action"` | Acción de migración: default `up`, aplica pendientes. Confirmaciones interactivas de rollback `down` y `reset` proponen **No** |
| 4. `"Execute"` | Ejecutar: aplica la acción. Tras `up`, puede ofrecer crear la primera organización si no existe |
| 5. `"Moonin API database Secret"` | Secret de base de API: ofrece crear/actualizar runtime, default **Sí**; reutilizar conexión de migraciones propone **Sí**. Elija **No** para otra cuenta/endpoint runtime |

El destino habitual runtime es `moonin/db-secret`. Actualizar un Secret de base existente propone **No**; aplicar el Secret revisado propone **Sí**. Confirme DNS accesible desde Pods, no `localhost` de la estación, y contenido PEM runtime. Consulte [modos TLS y claves](../preparation/) antes de aceptar. Si personaliza el Secret, alinee `moonin-api.databaseSecret.existingSecret`; el flujo normal Platform espera `moonin/db-secret`.

Las migraciones PostgreSQL embebidas registran versiones en `goose_db_version`, incluyendo metadata de routing ClickHouse. No crean las tablas de datos del motor analytics. Un Secret, release Helm correcta o hook de bootstrap no demuestra independientemente que el esquema PostgreSQL esperado esté aplicado.

### Cree la primera organización

Tras `up`, `"Create the first organization now"` (crear ahora la primera organización) propone **Sí** solo cuando no hay ninguna. Introduzca nombre, slug, correo propietario, dominio principal (propuesto desde el correo), tenant Entra, application/client ID, **valor del client secret** y authority host (normalmente `https://login.microsoftonline.com`). Entra es obligatorio en el bootstrap actual aunque el proveedor global de contraseña sea Cognito o Identity Platform.

Revise los datos no sensibles. `"Create the first organization"` (crear la primera organización) propone **No** antes de escribir. Al confirmar crea organización, dominio, administrador inicial y configuración Entra. El client secret se persiste en PostgreSQL: proteja base/backups. No registra una aplicación Entra ni verifica login de navegador extremo a extremo.

Para diferir bootstrap o separar automatización, con `DATABASE_URL` ya suministrada de forma segura y parámetros TLS incluidos:

```bash
moonin-installer migrate status
moonin-installer migrate up --skip-organization
moonin-installer bootstrap organization
```

Las acciones directas **no recorren el asistente TLS ni crean el Secret runtime**. Incluya `sslmode=verify-full`, `sslrootcert` y, para mTLS, rutas `sslcert`/`sslkey` según corresponda en la conexión inyectada. Use el flujo interactivo cuando necesite preparar el Secret runtime. Bootstrap explícito exige esquema y rechaza si ya existe una organización; cree las siguientes desde Admin. No repare bootstrap mediante escrituras SQL manuales.

## 4. Complete las nueve etapas Platform

```bash
moonin-installer platform install
```

Para un cambio productivo reproducible, fije una versión publicada real del chart. El archivo values opcional debe existir, estar revisado para ese chart y no contener secretos:

```bash
moonin-installer platform install \
  --version APPROVED_CHART_VERSION \
  --values /absolute/path/enterprise-values.yaml
```

Sustituya ambos marcadores. Los overrides prevalecen sobre valores generados; revise imágenes, seguridad, exposición y servicios en el plan final. No hay `--yes` global que vuelva desatendido este asistente.

### Etapa 1 de 9: Signed Moonin license

Licencia Moonin firmada: valida `moonin/moonin-license`, clave `MOONIN_LICENSE`, firma y caducidad. Reutilizar una existente válida propone **Sí**. Si falta o es inválida, pegue el JWS completo en el prompt protegido. Revise cliente, tipo, vigencia, funcionalidades y límites; el instalador no genera licencias ni imprime el texto completo.

### Etapa 2 de 9: Ingress controller

Controlador ingress: revise IngressClasses, controladores y clase default detectados. Reutilice ALB, NGINX, GCE, Traefik u otro compatible aprobado, o apruebe instalar Traefik `39.0.6` en `traefik-v2`. Revise balanceador privado/público en EKS. Una clase no demuestra acceso externo. Publicación ingress Platform, DNS y TLS se deciden después; aquí no se crean DNS ni certificados públicos.

### Etapa 3 de 9: NATS and JetStream

NATS y JetStream: reutilice release existente o apruebe chart oficial `nats/nats` `2.14.2`. Defaults nuevos: namespace `nats`, tres réplicas, PVC `50Gi` por réplica, stream `50Gi`, CPU request/limit `100m`/`1`, memoria `256Mi`/`2Gi` y límite Go `1600MiB`.

Personalizar capacidad propone **No**. Fijar una instalación nueva a etiqueta de nodo propone **No**. Elija StorageClass explícitamente; personalice réplicas impares, volúmenes, recursos o selector justificadamente. Revise nodos Ready y todas las zonas de PV existentes. No elige Spot u On-Demand silenciosamente. NATS se configura **antes** de elegir flujo rápido/personalizado Platform.

Una release externa se preserva. Registra progresivamente propiedad de una nueva para permitir reanudar. Puede proponer conservar selector existente. Reparaciones/resets proponen **No**: un reset pierde datos y no corrige ausencia de nodos compatibles. Diagnostique placement antes de una solución destructiva.

### Etapa 4 de 9: Moonin API PostgreSQL Secret

Secret PostgreSQL de API: busca `moonin/db-secret`, clave `DATABASE_URL`; reutilizar conexión utilizable propone **Sí**. Si falta, configure conexión runtime y TLS/mTLS. Asegure conectividad desde Pods y namespace correcto. La clave presente no valida red, privilegios ni esquema. Configura el Secret, no sustituye `migrate` local.

### Etapa 5 de 9: ClickHouse analytics connection

Conexión analytics: detecta `ClickHouseCluster` o acepta URI nativa externa. Guarda `moonin/moonin-clickhouse-connection`, clave `CLICKHOUSE_DSN`. Exige DSN válido para continuar, pero la sintaxis no prueba red/permisos. **No instala ClickHouse**. Repare la conexión por separado con `moonin-installer clickhouse connection` cuando proceda.

### Etapa 6 de 9: Moonin Portal authentication Secret

Secret de autenticación Portal: crea/actualiza `moonin/moonin-front-secret`. Ofrece `"Generate a secure NEXTAUTH session secret"` (generar secreto de sesión seguro) si falta; puede conservar configuración existente. Establezca `"Portal public URL"` a su URL aprobada, por ejemplo `https://portal.example.com`, y `"Cookie prefix"` a `moonin-portal`.

Configure proveedor email/contraseña y Google OAuth opcional. Google social nuevo comienza deshabilitado; `Keep current` conserva configuración existente en lugar de quitarla. Verifique credenciales, selección activa y callbacks con [autenticación](../authentication/). No acepte un host sugerido que no le pertenezca.

### Etapa 7 de 9: Admin UI authentication and internal service credentials

Autenticación Admin y credenciales internas: crea/actualiza `moonin/moonin-admin-ui-secret`. `"Reuse shared sign-in provider settings from Moonin Portal"` (reutilizar proveedores Portal) propone **Sí**, sincronizando claves de proveedor, reCAPTCHA y auto-verificación, **no sesiones**. Genere/conserve `NEXTAUTH_SECRET` Admin independiente, establezca `https://admin.example.com` e introduzca explícitamente prefijo `moonin-admin`. El selector común puede proponer `moonin-portal` en un Secret Admin nuevo: cámbielo.

Con Cognito activo, revise rol IAM de invitaciones y confianza del workload detectados/solicitados. Las credenciales AWS locales no autorizan Pods. Genera credenciales internas ausentes en `moonin-ai-delegation`, clave `secret`, y `moonin-chatbot`, clave `gateway-secret`; reutiliza existentes y exige confirmar rotación. Son distintas de AI Sync exclusivo SaaS.

### Etapa 8 de 9: Platform version and exposure

Versión y exposición: `"Use the recommended quick installation flow"` (usar flujo rápido recomendado) propone **Sí** tras prerrequisitos. Sin `--version`, rápido toma el chart publicado más reciente; personalizado pregunta versión y vacío toma más reciente. Fije una versión probada en producción. Muestra versión chart y appVersion por separado.

Ambos revisan placement y exposición. Rápido usa `ghcr-secret` existente; personalizado pregunta reutilización con default **Sí**. No referencia ni inventa un pull Secret ausente. Con licencia `customer`, Billing Sync y AI Sync permanecen deshabilitados en ambos.

Si hay release, actualizar a versión más nueva o reconciliar la misma propone **Sí**; downgrade o versión no comparable propone **No**. Una release ajena exige confirmar actualización y no pasa a ser eliminable por el instalador.

Decida publicación ingress, clase, dominio base y TLS. Reutilice un Secret TLS o créelo desde archivos PEM locales de certificado/cadena y clave; rutas interactivas admiten Tab. HTTP es una opción explícita para evitar HTTPS roto, **no una recomendación para login productivo**. Configure usted DNS, certificados y callbacks.

### Etapa 9 de 9: Review and deploy

Revisión y despliegue: revise destino, versiones chart/aplicación, imágenes, placement, ingress, TLS, servicios, overrides y cambios antes de confirmar. El dry-run Helm no imprime Secrets. Helm espera readiness y usa rollback atómico ante fallo de su operación.

Cambios anteriores de Secrets/dependencias y migraciones PostgreSQL quedan fuera. Después verifica chart e imágenes declaradas en recursos renderizados y plantillas vivas, incluidos init containers. Un fallo/mismatch posterior impide informar éxito, pero **no provoca rollback automático**. Inspeccione antes de reintentar. No demuestra el digest efectivo de todas las imágenes en ejecución.

Registra propiedad progresiva en `moonin/moonin-platform-install-state` como `created`, `reused` o `external`, sin contraseñas, JWS ni DSN. No lo borre ni edite para forzar propiedad o retirada. Cancelar al final no garantiza Kubernetes sin cambios.

## 5. Acepte el despliegue

```bash
moonin-installer platform status
moonin-installer clickhouse status
moonin-installer migrate status
kubectl -n moonin get pods,deployments,statefulsets,services,ingress,pvc
kubectl -n nats get pods,pvc
```

Omita estado ClickHouse interno para servicio externo; use sus verificaciones aprobadas. Estado de migraciones exige acceso desde la estación. Valide DNS/HTTPS, login/logout independientes Portal/Admin, permisos propietario, invitaciones/correo, acceso PostgreSQL/analytics e ingesta/consulta real. Helm `deployed` no es aceptación. Continúe con [autenticación](../authentication/) y la [lista de aceptación operativa](../operations/).