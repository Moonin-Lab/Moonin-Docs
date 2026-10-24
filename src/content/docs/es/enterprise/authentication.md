---
title: "Autenticación"
description: "Configure proveedores Portal/Admin, sesiones aisladas, callbacks Google e invitaciones Cognito opcionales."
sidebar:
  order: 5
---

Portal y Admin pueden compartir proveedores de identidad, pero deben tener sesiones de aplicación independientes. Entra a nivel de organización es distinto del proveedor global email/contraseña. Complete [preparación](../preparation/) y las etapas de [instalación](../installation/), o repare sus Secrets por separado con los comandos siguientes.

## Elija proveedores de login

`"Email/password setup"` (configuración email/contraseña) selecciona Identity Platform, Amazon Cognito o ambos. Con credenciales de ambos, **uno** está activo mediante `PASSWORD_AUTH_PROVIDER` (`identity-platform` o `cognito`); configurar dos no hace que ambos atiendan contraseña simultáneamente. Google OAuth social es independiente y puede coexistir con contraseña Cognito.

| Proveedor / ajuste | Claves que preparar | Notas |
| --- | --- | --- |
| Contraseña Identity Platform | `GOOGLE_IDENTITY_API_KEY`, `GOOGLE_PROJECT_ID` | Proyecto Google existente y servicio de identidad habilitado; no es cliente OAuth social |
| Contraseña Cognito | `COGNITO_REGION`, `COGNITO_USER_POOL_ID`, `COGNITO_CLIENT_ID`, `COGNITO_CLIENT_SECRET` | Pool y App Client compatibles existentes; región coherente con prefijo del pool |
| Google OAuth social | `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` | Cliente OAuth, consentimiento, orígenes y redirect URIs existentes |
| Proveedor activo | `PASSWORD_AUTH_PROVIDER` | Selecciona el backend de contraseña configurado utilizado |
| reCAPTCHA Enterprise opcional | `RECAPTCHA_API_KEY`, `RECAPTCHA_PROJECT_ID`, `RECAPTCHA_SITE_KEY` | Protección de registro separada, no proveedor de identidad ni sustituto MFA |
| Auto-verificación email | `AUTO_VERIFY_EMAIL_ON_SIGNUP` | Comienza `false`; habilitar omite prueba de propiedad del correo y exige aprobar el riesgo |

El descubrimiento AWS puede listar pools/clientes y obtener client secret solo si la identidad ya autenticada del operador está autorizada. Puede introducir datos manualmente. No provisiona pool, App Client, proyecto, cliente Google OAuth o aplicación Entra. Detectar correctamente no equivale a autorizar APIs de invitación para un Pod.

## Mantenga sesiones aisladas

| Ajuste | Portal | Admin |
| --- | --- | --- |
| Namespace / Secret | `moonin/moonin-front-secret` | `moonin/moonin-admin-ui-secret` |
| `NEXTAUTH_URL` | `https://portal.example.com` | `https://admin.example.com` |
| `NEXTAUTH_SECRET` | Secreto generado/aprobado independiente | Otro secreto generado/aprobado distinto |
| `NEXTAUTH_COOKIE_PREFIX` | `moonin-portal` | Elija explícitamente `moonin-admin` |

Las URLs son marcadores: reemplácelas por hosts HTTPS aprobados, sin ruta de aplicación. El instalador genera secretos de sesión ausentes y propone conservar existentes. Rotar uno invalida sesiones de esa aplicación; no inicia automáticamente sesión en la otra.

**Aviso para cookie Admin nueva:** Admin llama al mismo selector de prefijo que Portal. Si no existe prefijo, el default mostrado puede ser `moonin-portal`. Introduzca `moonin-admin` explícitamente. Aceptar proveedores compartidos no autoriza compartir nombres de cookie, URLs o secretos de cifrado/firma de sesión. Los prefijos admiten letras, números, guiones y guiones bajos.

Portal referencia `moonin-portal-ui.portalSecret.existingSecret` en el chart; alinee nombres y namespaces personalizados con el chart real. Admin usa su Secret independiente. Si falta `NEXTAUTH_SECRET` Admin, fallan las sesiones aunque todas las credenciales de proveedor existan.

## Configuración Portal y defaults

```bash
moonin-installer portal configure
```

El asistente independiente pregunta `"Portal namespace"` (namespace, default `moonin`) y `"Portal Secret name"` (nombre de Secret, default `moonin-front-secret`). Manténgalos salvo cambios coordinados del chart. Lee valores existentes y ofrece conservarlos.

| Prompt / decisión en inglés | Acción |
| --- | --- |
| `"Generate a secure NEXTAUTH session secret"` | Generar secreto de sesión: si falta, propone **Sí**; no reutilice el de Admin |
| `"Keep existing Portal public URL"` | Conservar URL pública: propone **Sí** si existe; si no, introduzca URL aprobada |
| `"Cookie prefix"` | Prefijo cookie: `moonin-portal`; conservar existente propone **Sí** |
| Google OAuth | Nuevo comienza deshabilitado; `Keep current` conserva credenciales existentes |
| `"Email/password setup"` | Elija backend(s), aporte credenciales emitidas por proveedor y revise cuál queda activo |
| `"Configure reCAPTCHA Enterprise for registration protection"` | Protección de registro: inicialmente deshabilitada sin configuración completa; aporte tres claves solo si el registro la utiliza |
| Aplicar Secret revisado | Revise destino y estado no sensible antes de aceptar |

En Identity Platform, `AUTO_VERIFY_EMAIL_ON_SIGNUP` comienza `false`; su flujo puede conservar un `true` existente. Cognito la fija en `false`. Prefiera verificación real de las cuentas Enterprise.

## Reutilización y reparación Admin

```bash
moonin-installer platform auth admin configure
```

Si existe Secret Portal, `"Reuse shared sign-in provider settings from Moonin Portal"` (reutilizar proveedores Portal) propone **Sí**. Copia selección activa, credenciales Identity Platform/Cognito, Google OAuth, reCAPTCHA y auto-verificación. Las claves compartidas ausentes en Portal se **eliminan de Admin** al sincronizar; revíselo si mantenía proveedores distintos intencionadamente.

Admin conserva/genera su propio `NEXTAUTH_SECRET`, solicita URL y prefijo cookie y, con Cognito activo, detecta/pide rol de invitaciones. `"Apply the Admin UI authentication Secret"` (aplicar Secret Admin) propone **Sí**. Rechace reutilización si Admin debe gestionar proveedores independientemente.

Cambiar Portal no sincroniza Admin en segundo plano. Ejecute otra vez Admin y acepte explícitamente cuando quiera sincronizar. Estos comandos actualizan Secrets, **no releases Helm ni procesos en ejecución**. Programe rollout/redeploy controlado de cada consumidor y compruebe readiness antes de probar. Las variables cargadas mediante `envFrom` no se renuevan en Pods existentes por cambiar un Secret.

## Dominios y callbacks Google

Prepare dominios autorizados en proyecto/identidad Google, orígenes del navegador y redirect URIs exactas. Para Google OAuth social, las rutas estándar NextAuth de los hosts de ejemplo son:

```text
Orígenes autorizados:
https://portal.example.com
https://admin.example.com

Redirect URIs autorizadas:
https://portal.example.com/api/auth/callback/google
https://admin.example.com/api/auth/callback/google
```

Use esquema/host externo real y ruta callback soportada por su aplicación desplegada. No registre un wildcard supuesto ni deje dominios sugeridos del servicio alojado. Si usa clientes Google distintos, registre callback de cada aplicación en su cliente y configure Admin independientemente en lugar de reutilizar credenciales a ciegas. Los dominios autorizados Identity Platform son un ajuste separado de los redirect URIs OAuth social.

Haga coincidir DNS, routing del balanceador, TLS ingress, `NEXTAUTH_URL`, OAuth y redirects Entra organizativos. El instalador guarda configuración; no provisiona cuentas ni demuestra propiedad de dominios. Pruebe login/logout desde las URLs reales del navegador.

## Cognito opcional: TOTP e invitaciones

Cognito es un **proveedor opcional**, no dependencia obligatoria de todo Enterprise. Si lo elige, configure TOTP de software y flujos esperados por las aplicaciones desplegadas. Un pool con MFA `OPTIONAL` admite enrollment TOTP por usuario; eso **no** permite que usuarios productivos no demo omitan las comprobaciones MFA del servidor de aplicación. Los flujos actuales de contraseña no demo exigen enrollment/desafíos MFA. Pruebe cambio de contraseña temporal, enrollment, códigos de seis dígitos, recuperación y reloj antes del despliegue.

Las identidades demo tienen comportamiento especial y pueden omitir controles normales. No habilite ni publique una cuenta demo Enterprise para evitar fallos de enrollment, email o MFA. Una cuenta privada de prueba debe ejercer la misma política que usuarios reales. Coordine recuperación MFA con identidad en lugar de debilitar el proveedor o modificar datos de usuarios manualmente.

Para invitaciones Admin en EKS, prepare rol IAM de workload mediante **IRSA**, independiente del login AWS CLI del operador. La confianza web identity debe referenciar OIDC del clúster, audiencia `sts.amazonaws.com` y sujeto exacto:

```text
system:serviceaccount:moonin:moonin-admin-ui
```

Conceda solo `cognito-idp:AdminCreateUser` y `cognito-idp:AdminGetUser`, acotadas al recurso del pool previsto. Anote el ServiceAccount Admin real con el rol aprobado mediante su proceso de infraestructura; el instalador detecta/pide ARN, no crea credenciales Pod copiando las de la estación. No inyecte claves AWS estáticas en Secrets de aplicación. Pod Identity de EBS CSI es un asunto separado de almacenamiento, no el modelo de confianza de invitaciones.

La plantilla Cognito debe incluir `{username}` y `{####}`. Prepare identidad remitente, SES si procede, restricciones sandbox, destinatarios autorizados, cuotas y entregabilidad. Un rol/pool existente no prueba entrega. Valide invitación a un usuario de prueba no demo aprobado y secuencia de primer login/contraseña/MFA.

## Aceptación de autenticación

1. Verifique HTTPS confiable en ambos hosts reales y ausencia de redirects a dominios no previstos.
2. Inicie sesión independientemente en Portal/Admin; pruebe logout y aislamiento cookie/sesión.
3. Confirme acceso propietario y límites organizativos, no solo autenticación exitosa en el proveedor.
4. Pruebe proveedor de contraseña activo, verificación email, MFA si aplica y Google opcional.
5. Pruebe autorización de invitaciones y recepción real; confirme que usuarios no autorizados no acceden.
6. Tras cambios de Secret, confirme redeploy y salud de consumidores. Elimine credenciales de evidencias diagnósticas.

Consulte [operaciones](../operations/) para reparación, planificación de reinicios y diagnóstico sin imprimir Secrets.