---
title: "Instalador Enterprise"
description: "Planifique, instale, proteja y opere Moonin Enterprise en Kubernetes bajo gestión del cliente."
sidebar:
  order: 1
---

Moonin Enterprise Installer guía al operador para desplegar la plataforma Moonin en su entorno Kubernetes. Necesita `moonin-installer` en el `PATH` de su estación y una licencia de cliente firmada proporcionada mediante onboarding Enterprise. Esta sección cubre la plataforma, no solamente los agentes instalados en clústeres monitorizados.

## Obtener el instalador más reciente

[Abrir el paquete Moonin Installer en GitHub Packages](https://github.com/Moonin-Lab/Moonin-Installer/pkgs/container/moonin-installer).

Este enlace permanente muestra las versiones publicadas sin requerir actualizaciones de la documentación. El paquete contiene archivos para Linux, macOS y Windows en `amd64` y `arm64`, además de `SHA256SUMS`. Es un paquete OCI de archivos, no un contenedor de aplicación.

### Descargar para su sistema operativo

Instale [ORAS CLI](https://oras.land/docs/installation/) y ejecute el comando de su sistema. Cada opción descarga solo su archivo y `SHA256SUMS`, no las demás plataformas. Son descargas OCI, no enlaces directos del navegador a ejecutables.

| Sistema operativo | Arquitectura | Comando de descarga |
| --- | --- | --- |
| Linux | Intel / AMD x86-64 | `oras pull ghcr.io/moonin-lab/moonin-installer:latest-linux-amd64 --output installer-download` |
| Linux | ARM64 | `oras pull ghcr.io/moonin-lab/moonin-installer:latest-linux-arm64 --output installer-download` |
| macOS | Intel | `oras pull ghcr.io/moonin-lab/moonin-installer:latest-darwin-amd64 --output installer-download` |
| macOS | Apple Silicon | `oras pull ghcr.io/moonin-lab/moonin-installer:latest-darwin-arm64 --output installer-download` |
| Windows | Intel / AMD x86-64 | `oras pull ghcr.io/moonin-lab/moonin-installer:latest-windows-amd64 --output installer-download` |
| Windows | ARM64 | `oras pull ghcr.io/moonin-lab/moonin-installer:latest-windows-arm64 --output installer-download` |

Tras descargar, verifique el archivo en macOS/Linux:

```bash
cd installer-download
shasum -a 256 -c SHA256SUMS
```

El pipeline de release actualiza los seis alias `latest-OS-ARCH` después de verificar todos los paquetes por plataforma, incluidas las versiones preliminares como `rc`. Estos alias estarán disponibles con la primera release que incluya ese cambio del pipeline; hasta entonces, seleccione un tag publicado en la página del paquete. El paquete conjunto `latest` sigue disponible para descargar los seis archivos. En Linux también puede usar `sha256sum --check SHA256SUMS`.

En Windows, verifique y extraiga mediante PowerShell:

```powershell
Set-Location installer-download
$checksum = (Get-Content SHA256SUMS -Raw).Trim() -split '\s+', 2
if ((Get-FileHash -LiteralPath $checksum[1] -Algorithm SHA256).Hash -ne $checksum[0]) {
  throw 'Checksum mismatch'
}
Expand-Archive -LiteralPath $checksum[1] -DestinationPath .\bin
.\bin\moonin-installer.exe version
```

En Linux/macOS, tras verificar correctamente el checksum, extraiga el archivo descargado con `tar -xzf ARCHIVO.tar.gz`, sustituyendo `ARCHIVO.tar.gz` por su nombre real. Ejecute `./moonin-installer version` antes de instalarlo en su `PATH`.

Extraiga solamente el archivo correspondiente a su sistema operativo y arquitectura y coloque el ejecutable en su `PATH`. No necesita Docker ni acceso al repositorio de código. Los paquetes públicos permiten descarga anónima; los privados requieren una cuenta GitHub autorizada y login con ORAS. No incluya tokens de acceso en esta documentación ni en argumentos de comandos.

`latest` puede cambiar y no significa última versión estable. En producción, utilice un tag de versión o digest aprobado, regístrelo y compruebe el binario extraído con `moonin-installer version`. Los checksums verifican integridad respecto al manifiesto, no autenticidad independiente del publicador.

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
- [Documentación Enterprise Installer en inglés](../../enterprise/)

La guía de agentes cubre otro alcance. Utilice endpoints y credenciales aprobados para su Enterprise, sin copiar a ella la configuración del servicio alojado.