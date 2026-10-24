---
title: "Instalador Enterprise"
description: "Planifique, instale, proteja y opere Moonin Enterprise en Kubernetes bajo gestión del cliente."
sidebar:
  order: 1
---

Moonin Enterprise Installer guía al operador para desplegar la plataforma Moonin en su entorno Kubernetes. Necesita `moonin-installer` en el `PATH` de su estación y una licencia de cliente firmada proporcionada mediante onboarding Enterprise. Esta sección cubre la plataforma, no solamente los agentes instalados en clústeres monitorizados.

## ¿SaaS o Enterprise?

| Modalidad | Alojamiento y operación | Cómo comenzar |
| --- | --- | --- |
| SaaS | Moonin aloja y opera la plataforma; su equipo conecta los clústeres que desea monitorizar | Utilice el servicio alojado de Moonin según su suscripción. No instala la plataforma Enterprise con esta CLI |
| Enterprise | Su organización despliega y opera la plataforma en su propio entorno Kubernetes, incluida infraestructura, seguridad, backups y actualizaciones | Contacte a Ventas de Moonin para obtener una licencia Enterprise y acordar el alcance antes de instalar |

:::caution[Enterprise requiere una licencia comercial]
Descargar la CLI no constituye una licencia Enterprise ni concede el derecho de desplegar o utilizar la plataforma Enterprise. **Debe contactar a Ventas de Moonin para obtener una licencia de cliente Enterprise firmada antes de instalar.** Si aún no tiene un contacto comercial, solicítelo mediante su representante de cuenta o el sitio web oficial de Moonin. Descargar o ejecutar el instalador no genera una licencia.
:::

### Cómo funciona la licencia Enterprise

1. Contacte a Ventas indicando el despliegue previsto, la capacidad monitorizada y las funcionalidades necesarias. Acuerde alcance, vigencia, soporte y condiciones comerciales; esta guía no fija precios ni implica una prueba gratuita.
2. Moonin proporciona una licencia firmada de tipo `customer` mediante onboarding Enterprise. Sus campos firmados definen cliente, vigencia, funcionalidades habilitadas y capacidad contratada. No edite los campos: cualquier modificación invalida la firma.
3. Introduzca el JWS firmado completo durante la instalación o use `moonin-installer license install`. Se almacena por defecto en el Secret Kubernetes `moonin/moonin-license`, clave `MOONIN_LICENSE`. El instalador comprueba firma y caducidad antes de aceptarla; el binario descargado no es una credencial de activación.
4. Gestione la renovación con Ventas antes del vencimiento y solicite una licencia nueva para cambios acordados de capacidad o funcionalidades. Instale la sustitución con el mismo comando de licencia y compruebe el estado resultante. No presuponga un período de gracia ni que una licencia caducada, ausente o inválida permita continuar operando.

La capacidad se expresa en Compute Units (CU): el mayor entre las vCPU declaradas agregadas y la mitad de la RAM declarada en GB decimales, redondeado hacia arriba. La validación actual de licencias de cliente también espera almacenamiento incluido de `10 GB × CU`; ese derecho no aprovisiona discos ni garantiza retención. Consulte la [preparación de la licencia](preparation/) para la fórmula exacta, el alcance y el manejo seguro. La disponibilidad de descarga, la vigencia de la licencia y la versión del chart Platform son cuestiones independientes.

## Obtener el instalador más reciente

[Abrir las releases públicas de Moonin Installer](https://github.com/Moonin-Lab/Moonin-Installer-Releases/releases).

Este es el único canal público de distribución. El repositorio de código sigue siendo privado. Cada release contiene archivos para Linux, macOS y Windows en `amd64` y `arm64`, además de `SHA256SUMS` y `RELEASE.txt`.

### Descargar para su sistema operativo

Descargue directamente en el navegador, sin autenticación ni acceso al repositorio privado del código:

| Sistema operativo | Intel / AMD x86-64 | ARM64 |
| --- | --- | --- |
| Linux | [Descargar Linux x86-64](https://github.com/Moonin-Lab/Moonin-Installer-Releases/releases/download/preview/moonin-installer_linux_amd64.tar.gz) | [Descargar Linux ARM64](https://github.com/Moonin-Lab/Moonin-Installer-Releases/releases/download/preview/moonin-installer_linux_arm64.tar.gz) |
| macOS | [Descargar macOS Intel](https://github.com/Moonin-Lab/Moonin-Installer-Releases/releases/download/preview/moonin-installer_darwin_amd64.tar.gz) | [Descargar macOS Apple Silicon](https://github.com/Moonin-Lab/Moonin-Installer-Releases/releases/download/preview/moonin-installer_darwin_arm64.tar.gz) |
| Windows | [Descargar Windows x86-64](https://github.com/Moonin-Lab/Moonin-Installer-Releases/releases/download/preview/moonin-installer_windows_amd64.zip) | [Descargar Windows ARM64](https://github.com/Moonin-Lab/Moonin-Installer-Releases/releases/download/preview/moonin-installer_windows_arm64.zip) |

Estas URL permanentes siguen **preview**, incluidas las versiones candidatas, no versiones estables certificadas. [Consulte la versión del canal](https://github.com/Moonin-Lab/Moonin-Installer-Releases/releases/tag/preview) y descargue [SHA256SUMS](https://github.com/Moonin-Lab/Moonin-Installer-Releases/releases/download/preview/SHA256SUMS). Compare el SHA-256 de su archivo con su entrada exacta antes de extraerlo: use `shasum -a 256 ARCHIVO` en macOS, `sha256sum ARCHIVO` en Linux o `Get-FileHash -Algorithm SHA256 ARCHIVO` en Windows, sustituyendo `ARCHIVO` por su nombre. Si difiere, descarte el archivo y descargue archivo y manifiesto desde la misma release versionada.

Para descargas productivas reproducibles, elija una versión aprobada entre [todas las releases](https://github.com/Moonin-Lab/Moonin-Installer-Releases/releases). El canal separado `stable` se publica únicamente con versiones no preliminares. Los enlaces estarán disponibles tras la primera ejecución correcta del pipeline de distribución pública; crear el repositorio por sí solo no publica binarios.

### Verificar, extraer y añadir al PATH

Guarde su archivo y `SHA256SUMS` en una carpeta `installer-download`. El manifiesto tiene seis entradas: verifique solamente el nombre exacto del archivo descargado, no el manifiesto completo ni su primera línea. En Linux/macOS, ajuste `ASSET` al nombre de su archivo:

```bash
set -eu
cd installer-download
ASSET='moonin-installer_darwin_arm64.tar.gz'
CHECKSUM=$(awk -v asset="$ASSET" '$2 == asset { entry = $0; count++ } END { if (count != 1) exit 1; print entry }' SHA256SUMS)
printf '%s\n' "$CHECKSUM" | shasum -a 256 -c -
tar -xzf "$ASSET" moonin-installer
./moonin-installer version
mkdir -p "$HOME/.local/bin"
install -m 0755 moonin-installer "$HOME/.local/bin/moonin-installer"
export PATH="$HOME/.local/bin:$PATH"
moonin-installer version
```

En Linux puede sustituir `shasum -a 256 -c -` por `sha256sum -c -`. Si falta la entrada, está duplicada o falla la verificación, no continúe. Añada `export PATH="$HOME/.local/bin:$PATH"` al archivo de inicio de su shell (por ejemplo, `~/.zshrc` o `~/.bashrc`) para conservarlo en nuevas sesiones.

En Windows, seleccione el nombre de su ZIP y ejecute en PowerShell:

```powershell
$ErrorActionPreference = 'Stop'
Set-Location installer-download
$asset = 'moonin-installer_windows_amd64.zip'
$pattern = '^[0-9a-fA-F]{64}\s+\*?' + [regex]::Escape($asset) + '$'
$entries = @(Get-Content -LiteralPath SHA256SUMS | Where-Object { $_ -match $pattern })
if ($entries.Count -ne 1) { throw 'Expected exactly one checksum entry' }
$expected = ($entries[0] -split '\s+', 2)[0]
if ((Get-FileHash -LiteralPath $asset -Algorithm SHA256).Hash -ne $expected) {
  throw 'Checksum mismatch'
}
$binDir = Join-Path $env:LOCALAPPDATA 'Moonin\bin'
Expand-Archive -LiteralPath $asset -DestinationPath $binDir -Force
& (Join-Path $binDir 'moonin-installer.exe') version
$userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
if ($binDir -notin ($userPath -split ';')) {
  [Environment]::SetEnvironmentVariable('Path', "$binDir;$userPath", 'User')
}
$env:Path = "$binDir;$env:Path"
moonin-installer version
```

El `PATH` de usuario de Windows persiste en nuevos terminales; la última asignación también actualiza la sesión actual. Extraiga solamente el archivo de su sistema operativo y arquitectura. No necesita Docker ni acceso al repositorio de código.

Tanto `preview` como `stable` pueden cambiar. En producción, registre un tag de release versionada aprobado y compruebe el binario extraído con `moonin-installer version`. Los checksums verifican integridad respecto al manifiesto, no autenticidad independiente del publicador. Tras completar la preparación, inicie el asistente con `moonin-installer platform install`.

## Recorrido de instalación

1. Compruebe los [requisitos](requirements/): herramientas, compatibilidad Kubernetes, almacenamiento, permisos y dimensionamiento preliminar.
2. Complete la [preparación](preparation/): licencia, endpoints privados de bases de datos, certificados, aplicaciones de identidad y administrador de la organización inicial.
3. Siga la [instalación](installation/): prepare ClickHouse, migre PostgreSQL, cree la primera organización y complete las nueve etapas de Platform.
4. Valide la [autenticación](authentication/): sesiones separadas de Portal y Admin, callbacks y, opcionalmente, invitaciones Cognito.
5. Consulte [operaciones](operations/) para aceptación, renovación de licencia, reparación de configuración, actualizaciones, diagnóstico y retirada controlada.

Los ejemplos usan sintaxis Bash. Las variantes de estación Linux, macOS y Windows admiten `amd64` y `arm64`; utilice la proporcionada para su sistema y arquitectura. En Windows, adapte sintaxis, comillas, variables de entorno y rutas a PowerShell. La arquitectura de la estación no garantiza que todas las imágenes de Platform admitan sus nodos Kubernetes.

```bash
moonin-installer version
moonin-installer --help
moonin-installer platform install --help
```

Registre la versión del Installer por separado de la versión del chart Platform y sus versiones de aplicación/imágenes. No son intercambiables. Consulte la ayuda del comando suministrado para conocer los flags de esa versión.

## Límites del despliegue

| Capa | Responsabilidad |
| --- | --- |
| Infraestructura del cliente | Kubernetes, red privada, PostgreSQL, DNS, certificados, almacenamiento durable, identidades de workload aprobadas, backups y aplicaciones de identidad |
| Dependencias guiadas | Reutilizar o configurar ingress y NATS; instalar opcionalmente ClickHouse, Keeper, cert-manager y ClickHouse Operator |
| Configuración Platform | Secrets de licencia y conexiones, autenticación Portal/Admin, placement, versión del chart, exposición y despliegue Helm revisado |
| Operación posterior | Pruebas funcionales, monitorización, retención, ejercicios de recuperación, gobierno de cuentas y mantenimiento controlado |

El instalador no crea su clúster, PostgreSQL/RDS, VPC, certificados públicos, registros DNS, pools Cognito ni aplicaciones Google o Entra. En EKS, una ruta de ayuda de almacenamiento con confirmación independiente puede crear o reutilizar IAM, Pod Identity, EBS CSI y StorageClass. Trátela como cambio de infraestructura sujeto a aprobación, no como reparación implícita de un prerrequisito.

La secuencia de dependencias es:

```text
Estación + contexto Kubernetes autorizado
  -> almacenamiento durable + red + PostgreSQL + identidad + licencia de cliente
  -> ClickHouse externo O asistente de instalación ClickHouse
  -> migraciones PostgreSQL + primera organización
  -> asistente Platform de nueve etapas
  -> HTTPS + autenticación + aceptación de ingesta/consulta
```

Con ClickHouse externo se omite `clickhouse install`, no la configuración de conexión. La etapa de conexión ClickHouse de Platform no instala el motor analytics ni sustituye las migraciones PostgreSQL. El onboarding de agentes en clústeres monitorizados es una tarea posterior a la aceptación de la plataforma.

## Licencia de cliente y alcance

Una licencia `customer` firmada habilita el despliegue del cliente conforme a su vigencia, funcionalidades y capacidad. Billing Sync y AI Sync son servicios de sincronización exclusivos de SaaS y permanecen deshabilitados con licencias de cliente tanto en instalación rápida como personalizada. Esto no significa que toda funcionalidad relacionada con IA esté deshabilitada; depende de las funcionalidades licenciadas y los servicios configurados.

El instalador no certifica capacidad ni constituye un diseño de alta disponibilidad. En particular, la topología inicial de ClickHouse y Keeper tiene una réplica de cada uno. Revise las tablas de recursos y las restricciones de producción en [requisitos](requirements/) antes de aprobar el despliegue.

## Modelo de seguridad

Los Secrets son sensibles aunque estén almacenados en Kubernetes. Aplique RBAC por namespace, cifrado en reposo, acceso controlado al terminal y protección de backups. No incluya contraseñas, conexiones con credenciales, licencias firmadas ni claves privadas en values, argumentos, tickets o Git. No todas las entradas de texto están enmascaradas; no grabe sesiones de introducción de credenciales ni active trazas del shell.

La instalación completa **no es una transacción única**. Las etapas anteriores pueden modificar Secrets o instalar dependencias antes de la revisión final. Cancelarla no deshace esos cambios. El rollback atómico de Helm cubre su propia operación fallida, no etapas anteriores, migraciones externas ni fallos de verificaciones posteriores. Consulte los límites de aprobación en [instalación](installation/).

## Documentación relacionada

- [Arquitectura del producto](../getting-started/architecture/)
- [Instalación de agentes en clústeres monitorizados](../getting-started/installation/)
- [Documentación Enterprise Installer en inglés](https://docs.moonin.app/enterprise/)

La guía de agentes cubre otro alcance. Utilice endpoints y credenciales aprobados para su Enterprise, sin copiar a ella la configuración del servicio alojado.