---
title: "Preparación"
description: "Prepare licencia de cliente, seguridad de bases de datos, identidad, DNS y decisiones de despliegue."
sidebar:
  order: 3
---

Empiece tras completar los [requisitos](../requirements/). Acuerde responsable de instalación, aprobador de infraestructura, DBA, administrador de identidad, responsable de backups y ventana de mantenimiento. Registre decisiones no sensibles en el cambio; conserve credenciales solo en sistemas aprobados de gestión de secretos.

## 1. Prepare la licencia de cliente firmada

Obtenga una licencia `customer` firmada y vigente mediante onboarding Enterprise. Prepare el JWS completo para entrada interactiva, no una ruta de archivo. Compruebe cliente, fechas, funcionalidades, capacidad, almacenamiento y soporte. El instalador valida firma y caducidad; no genera licencias.

Las unidades de cómputo (CU) expresan el mayor valor entre CPU agregada y memoria dividida entre dos, redondeando hacia arriba:

```text
CU = max(ceil(vCPU agregadas), ceil(RAM agregada en GB decimales / 2))
Campos exactos de licencia:
CU = max(ceil(declared_vcpu_millicores / 1000), ceil(declared_memory_mb / 2000))
```

Por ejemplo, declarar 12 vCPU y 48 GB decimales RAM corresponde a `max(12, 24) = 24 CU`. Agregue el ámbito de capacidad acordado en su licencia; no lo sustituya silenciosamente por límites Kubernetes, capacidad allocatable o cálculo por nodo. Los MB/GB decimales de licencia no son MiB/GiB Kubernetes. La validación de cliente también espera almacenamiento incluido de `10 GB × CU`; ese derecho no representa PVC provisionados ni retención efectiva. Confirme contrato firmado y ámbito con onboarding en lugar de editar claims.

Platform valida `moonin/moonin-license`, clave `MOONIN_LICENSE`. Puede instalarla o renovarla por separado con `moonin-installer license install`; una licencia válida existente puede reutilizarse al instalar Platform. No incluya el JWS en argumentos, values, capturas o logs. Billing Sync y AI Sync permanecen deshabilitados para `customer`; no habilite sincronización SaaS para resolver un problema de licencia.

## 2. Reserve nombres, versiones y endpoints

| Decisión | Preparación |
| --- | --- |
| Contexto Kubernetes | Destino y permisos aprobados; reconfirme inmediatamente antes de escribir |
| Chart Platform | Versión publicada real probada con sus dependencias; registre aparte versiones de aplicación/imágenes |
| Namespaces | Platform usa por defecto `moonin`; ClickHouse `moonin-clickhouse`; NATS `nats` |
| DNS de usuario | Por ejemplo `portal.example.com` y `admin.example.com`, con ingress, responsables DNS y certificados HTTPS |
| PostgreSQL | Base dedicada Moonin, endpoint privado, cuenta de migración y runtime, bundle CA, mTLS opcional |
| ClickHouse | Servicio externo de protocolo nativo o stack interno previsto; permisos de base/usuario, TLS, capacidad y backups |
| NATS | Servicio compatible existente o instalación JetStream de tres réplicas aprobada, StorageClass, placement y retención |
| Imágenes | Acceso al registro y pull Secret existente si lo requieren las imágenes elegidas |

Los nombres `example.com` de esta sección son marcadores. Introduzca sus hosts aprobados en lugar de aceptar cualquier URL pública sugerida por el asistente. Planifique conjuntamente clase ingress, balanceador privado/público, dominio base, Secret TLS y cadena de certificados. El instalador no crea DNS ni emite certificados públicos.

## 3. Prepare PostgreSQL y su transporte

Cree una base dedicada Moonin API, **no** una base Keycloak o de otra aplicación. La cuenta de migración necesita permisos para tablas, funciones, triggers y extensiones requeridas; confirme restricciones del servicio gestionado con el DBA. La cuenta runtime puede ser distinta y más limitada. Ambas necesitan los permisos y rutas correspondientes, pero las migraciones parten de la estación y runtime de los Pods.

Prefiera `verify-full` con CA confiable y nombre DNS de base presente en el certificado. En RDS, obtenga el bundle CA oficial de AWS mediante su proceso aprobado, compruebe origen y vigencia y prepare su ruta PEM local. No sustituya una CA arbitraria ni desactive la verificación de hostname para ocultar errores.

| Selección TLS | Significado |
| --- | --- |
| `disable` | Transporte sin cifrar; inadecuado en redes no confiables |
| `require` | Exige cifrado; no equivale a verificar explícitamente CA y hostname |
| `verify-ca` | Valida la cadena del servidor contra la CA proporcionada |
| `verify-full` | Valida cadena y hostname de base; preferido con DNS y certificados correctos |

El asistente deriva la elección TLS inicial de la URL de conexión. No existe un default universal seguro que sustituya su revisión. mTLS opcional necesita certificado de cliente y clave privada aceptados por la base. Proteja permisos locales de la clave y el procedimiento de renovación.

Las migraciones usan rutas locales de CA/certificado. Para runtime, el instalador almacena el **contenido** PEM, no rutas de la estación, en un Secret del namespace:

| Secret por defecto | Clave | Contenido |
| --- | --- | --- |
| `moonin/db-secret` | `DATABASE_URL` | URL de conexión runtime |
| `moonin/db-secret` | `DATABASE_TLS_CA_PEM` | Bundle CA cuando procede |
| `moonin/db-secret` | `DATABASE_TLS_CLIENT_CERT_PEM` | Certificado mTLS opcional |
| `moonin/db-secret` | `DATABASE_TLS_CLIENT_KEY_PEM` | Clave privada mTLS opcional |

No copie sin cambios una conexión de estación con `localhost` a través de un túnel al runtime. Dentro de un Pod, `localhost` es ese Pod. El túnel también puede romper la verificación de hostname; use un diseño aprobado que preserve la identidad del certificado, sin debilitar TLS. Los nombres de Secret personalizados deben coincidir con el chart; un Pod en `moonin` no consume directamente un Secret de otro namespace.

## 4. Prepare la primera organización

El bootstrap inicial de la CLI actual exige Microsoft Entra ID **aunque el login email/contraseña de Portal/Admin use Cognito o Identity Platform**. Son capas de configuración diferentes. Prepare antes de `migrate`:

| Dato | Preparación necesaria |
| --- | --- |
| Nombre y slug | Nombre visible y slug único acordados |
| Correo del administrador propietario | Administrador responsable válido, por ejemplo `owner@example.com` |
| Dominio principal | Habitualmente el del correo; verifique propiedad y límite organizativo previsto |
| Entra tenant ID | Tenant existente preparado por identidad |
| Application/client ID | Registro de aplicación existente con configuración aprobada |
| Client secret | El **valor** del secreto, no su identificador; vigente y con plan de renovación |
| Authority host | Normalmente `https://login.microsoftonline.com`; use la autoridad aprobada para tenant/cloud |

El instalador no crea la aplicación Entra ni demuestra un login completo por guardar estos datos. Bootstrap no imprime ni guarda localmente el client secret, pero **sí lo persiste en PostgreSQL**. Proteja base y backups. Puede diferir la organización con `migrate up --skip-organization` y ejecutar después `bootstrap organization`, pero ello no elimina el requisito actual de Entra.

## 5. Prepare identidades Portal y Admin

Elija Identity Platform, Cognito o ambos con un proveedor email/contraseña activo. Google OAuth social es independiente y puede coexistir con cualquiera. Prepare aplicaciones, credenciales, dominios autorizados, callbacks de Portal y Admin y entrega de correo probada. El instalador no provisiona esas aplicaciones de identidad.

Use dos secretos de sesión, URLs públicas distintas y prefijos de cookie diferentes aunque reutilice credenciales de proveedor. Revise tabla completa de claves, ejemplos de callbacks Google, TOTP opcional de Cognito y rol de invitaciones en [autenticación](../authentication/).

Para Cognito en EKS, prepare un rol IAM de workload para invitaciones Admin, no credenciales AWS estáticas. Sus permisos deben limitarse al pool previsto y su confianza al ServiceAccount Admin. La sesión AWS local del operador no se transfiere a Pods.

## 6. Apruebe almacenamiento, recuperación y overrides

Acuerde StorageClass, selectores compatibles con zonas, pools estables, tamaños de volumen, retención y margen. La topología default de una réplica ClickHouse/Keeper no es HA. Confirme horarios, responsables y pruebas de restauración PostgreSQL, ClickHouse y JetStream y objetivos de recuperación antes de tráfico productivo.

Si proporciona values, use un archivo local existente, revisado para el chart y **sin secretos**. Los overrides explícitos prevalecen sobre valores generados, incluso en seguridad, imágenes y servicios habilitados. No use values para eludir el modo de despliegue de la licencia firmada.

Confirme acceso a fuentes y registros, compatibilidad de controladores y aprobación de cualquier configuración EKS CSI. Registre propiedad de recursos para evitar borrar infraestructura compartida al retirar. Continúe con [instalación](../installation/).