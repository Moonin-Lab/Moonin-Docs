---
title: "Requisitos"
description: "Software, acceso, red, almacenamiento y dimensionamiento preliminar para una instalación Enterprise."
sidebar:
  order: 2
---

Complete estas comprobaciones antes de la [preparación](../preparation/). La compatibilidad de infraestructura y software es obligatoria; la recomendación de hardware es orientativa, no un mínimo certificado.

## Estación del operador

| Dependencia | Requisito y finalidad |
| --- | --- |
| Enterprise Installer | Proporcionado mediante onboarding Enterprise, en `PATH`, para Linux/macOS/Windows y `amd64`/`arm64` correspondientes |
| `kubectl` | Obligatorio, con kubeconfig autorizado y versión de cliente compatible con el servidor Kubernetes |
| Git | Obligatorio: Platform obtiene mediante Git la versión seleccionada de su chart |
| Helm CLI | Obligatorio para instalar ClickHouse y sus dependencias; use **Helm 3.15+ como referencia de planificación**, verificando después los requisitos de los charts elegidos. Platform integra el SDK de Helm |
| AWS CLI | Opcional para descubrimiento AWS y la ruta confirmada de almacenamiento EKS; debe estar previamente autenticada y autorizada si se utiliza |
| Archivos PEM locales | Bundle CA confiable y, solo cuando se requiera, certificado/clave privada de cliente para mTLS PostgreSQL; cadena/clave de ingress si se crea un Secret TLS |
| Go y Docker | **No son necesarios para el usuario final** para ejecutar el instalador suministrado ni operar este recorrido |

Use los ejemplos Bash en Linux/macOS o adáptelos a PowerShell en Windows. Estas comprobaciones no modifican recursos del clúster:

```bash
moonin-installer version
moonin-installer --help
kubectl version --client
git --version
helm version --short
kubectl config current-context
kubectl config get-contexts
kubectl get nodes
kubectl get storageclass
kubectl get ingressclass
```

Confirme el contexto previsto antes de escribir. Si procede, seleccione uno aprobado con `kubectl config use-context APPROVED_CONTEXT`. `platform install` usa el contexto activo y no tiene un flag específico `--context`. Nunca comparta la salida de un kubeconfig sin filtrar.

## Kubernetes y permisos

La referencia documentada por el chart Platform es **Kubernetes 1.25**, pero **no garantiza** que las dependencias actuales funcionen en Kubernetes 1.25. Elija una versión Kubernetes con soporte vigente y compatible con el chart Platform, controlador ingress, chart NATS, cert-manager, ClickHouse Operator, driver CSI y proveedor cloud seleccionados. Verifique metadata y políticas de soporte de las versiones realmente instaladas; no despliegue un clúster sin soporte porque un chart acepte su versión.

El operador necesita consultar namespaces, nodos, IngressClasses, StorageClasses, PV, PVC, releases y Secrets pertinentes, y crear/actualizar workloads, Services, configuración, Secrets e ingress seleccionados. Instalar dependencias ClickHouse puede requerir CRDs y RBAC de alcance de clúster. Solicite permisos acotados al administrador; esta guía no prescribe acceso permanente `cluster-admin`.

Disponga de nodos Ready, capacidad **allocatable** suficiente tras las reservas del sistema, CNI y DNS funcionales, provisioner CSI dinámico con soporte y StorageClass utilizable. Es posible reutilizar controladores ingress, cert-manager y ClickHouse Operator compatibles. Una IngressClass no demuestra que exista un balanceador accesible.

## Recomendación preliminar de cómputo

El código del instalador **no establece un mínimo de hardware certificado**. Para una prueba de concepto preliminar, con tráfico modesto y todas las dependencias dentro del clúster, planifique **tres workers de 4 vCPU y 16 GiB RAM cada uno**. No es un mínimo contractual, promesa de rendimiento ni configuración HA. Los workloads del sistema, componentes Platform habilitados, bases de datos, margen de actualización, fallos de nodo y tasas reales de telemetría pueden exigir bastante más capacidad.

Si PostgreSQL es gestionado fuera del clúster, su capacidad es adicional y se dimensiona aparte. Incluso con tres workers, una réplica ClickHouse y una Keeper siguen siendo puntos únicos de fallo. Producción exige medir ingesta, consultas concurrentes, retención, compresión, ráfagas, replicación de streams y objetivos de recuperación. Mida CPU, memoria, utilización/latencia de disco, profundidad de colas y rendimiento de ingesta/consulta durante la aceptación, y amplíe requests o capacidad antes de saturar.

## Recursos iniciales por defecto

Son defaults de dependencias, **no el presupuesto total de Platform**. Los requests reservan capacidad de scheduling; los límites no garantizan recursos disponibles. CPU y memoria son por réplica.

| Componente | Réplicas | CPU request / limit | Memoria request / limit | Capacidad PVC solicitada |
| --- | --- | --- | --- | --- |
| NATS / JetStream | 3 | `100m` / `1` | `256Mi` / `2Gi` | `50Gi` cada uno, `150Gi` total |
| ClickHouse | 1 | `1` / `4` | `2Gi` / `8Gi` | `100Gi` |
| Keeper | 1 | `100m` / `500m` | `256Mi` / `512Mi` | `10Gi` |

NATS también comienza con capacidad de stream `50Gi` y límite de memoria Go `1600MiB`. No equipare la capacidad del stream con disco utilizable garantizado tras overhead de filesystem y operación.

La suma inicial es **3 × 50Gi + 100Gi + 10Gi = 260Gi únicamente de capacidad lógica solicitada en PVC**. Excluye PostgreSQL, overhead de filesystem/base de datos, replicación del proveedor, backups, snapshots, réplicas adicionales, otros volúmenes Platform y margen libre. No es retención útil de telemetría ni facturación física completa de almacenamiento. Las réplicas adicionales de streams consumen almacenamiento adicional dentro de la topología; aumentar retención sin dimensionar disco y escritura puede agotar capacidad.

## Almacenamiento durable y scheduling

Seleccione StorageClass explícitamente. ClickHouse propone la clase default o una `WaitForFirstConsumer` si no existe default, rechaza provisioners in-tree antiguos y espera CSI registrado o provisioners dinámicos modernos compatibles. El almacenamiento local al nodo puede servir en desarrollo desechable; no sustituye almacenamiento durable productivo.

Planifique expansión, reclaim policy, backups, recuperación, IOPS/throughput y afinidad de zona. `WaitForFirstConsumer` ayuda en el scheduling inicial; no reubica volúmenes existentes. Los selectores deben coincidir con nodos Ready y las zonas de **todos** los PV existentes. Reserve margen para drains y actualizaciones progresivas.

Para dependencias durables, prefiera un pool estable aprobado, habitualmente On-Demand. Interrupciones Spot pueden afectar quorum, ingesta o recuperación; un selector no es una política de durabilidad. El instalador no elige Spot u On-Demand silenciosamente. Si usa capacidad interrumpible, diseñe placement, presupuestos de interrupción, distribución de réplicas y recuperación. Tres réplicas NATS no prueban por sí solas distribución entre zonas ni HA extremo a extremo.

## Red y servicios dependientes

| Trayecto | Acceso necesario |
| --- | --- |
| Estación → Kubernetes | Endpoint API y renovación de autenticación/autorización |
| Estación → PostgreSQL | DNS/routing privado, VPN o túnel aprobado para migraciones; puerto real, habitualmente `5432` |
| Pods → PostgreSQL | Conectividad runtime independiente; el túnel de la estación no da conectividad a los Pods |
| Consumidores Platform → ClickHouse | Endpoint de protocolo nativo, habitualmente `9000` o TLS `9440`, según proveedor |
| Pods → NATS | Acceso al servicio interno y políticas aprobadas para productores/consumidores JetStream |
| Estación/clúster → dependencias | Fuentes Git/charts/operator y registros de imágenes aprobados; no es un flujo air-gapped completo |
| Navegadores → Portal/Admin | DNS, ingress/balanceador, HTTPS confiable y callbacks de identidad |
| Workloads → identidad/correo | Endpoints del proveedor y, para invitaciones, APIs cloud autorizadas y entrega de correo funcional |

No exponga PostgreSQL, ClickHouse o NATS públicamente solo para completar la instalación. Aplique rutas privadas, firewall/security groups y NetworkPolicies conforme a puertos y workloads elegidos. Planifique HTTPS para login productivo y TLS verificado, opcionalmente mTLS, para bases de datos. Continúe con [preparación](../preparation/).