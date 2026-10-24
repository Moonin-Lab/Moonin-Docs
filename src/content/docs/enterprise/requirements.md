---
title: "Requirements"
description: "Mandatory software, access, networking, storage, and preliminary sizing for an Enterprise installation."
sidebar:
  order: 2
---

Complete these checks before [preparation](../preparation/). Infrastructure and software compatibility are mandatory; the hardware recommendation below is preliminary guidance, not a certified minimum.

## Operator workstation

| Dependency | Requirement and purpose |
| --- | --- |
| Enterprise Installer | Provided through enterprise onboarding, in `PATH`, matching Linux/macOS/Windows and `amd64`/`arm64` |
| `kubectl` | Required with authorized kubeconfig and a client version supported by your Kubernetes server |
| Git | Required: Platform obtains the selected version of its chart through Git |
| Helm CLI | Required for the ClickHouse installation path and its dependencies; use Helm **3.15+ as a planning baseline**, then verify the actual selected charts' requirements. Platform uses an integrated Helm SDK |
| AWS CLI | Optional for AWS discovery and the confirmed EKS storage setup path; it must already be authenticated and authorized if used |
| Local PEM files | Trusted CA bundle and, only when required, client certificate/private key for PostgreSQL mTLS; ingress certificate chain/key if creating a TLS Secret |
| Go and Docker | **Not required by the end user** to run the supplied installer or operate this installation flow |

Use Bash examples on Linux/macOS or adapt them to PowerShell on Windows. These checks do not change cluster resources:

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

Confirm the intended context before any write. If necessary, select an approved context with `kubectl config use-context APPROVED_CONTEXT`. `platform install` uses the active context and has no dedicated `--context` flag. Never share raw kubeconfig output.

## Kubernetes and permissions

The Platform chart's documented Kubernetes baseline is **1.25**, but that is **not a guarantee** that current dependencies run on Kubernetes 1.25. Choose a currently supported Kubernetes release compatible with the selected Platform chart, ingress controller, NATS chart, cert-manager, ClickHouse Operator, CSI driver, and cloud provider. Verify chart metadata and dependency support policies for the versions actually installed; do not deploy an unsupported cluster because a chart accepts its version string.

The operator needs permission to inspect namespaces, nodes, IngressClasses, StorageClasses, PVs, PVCs, releases, and relevant Secrets, and to create/update the selected workloads, Services, configuration, Secrets, and ingress resources. Installing ClickHouse dependencies can require cluster-scoped CRDs and RBAC. Ask the cluster administrator for scoped permissions; this guide does not prescribe permanent `cluster-admin` access.

Provide Ready nodes, sufficient **allocatable** capacity after system reservations, a working CNI and cluster DNS, a supported dynamic CSI provisioner, and a usable StorageClass. Existing ingress controllers, cert-manager, and ClickHouse Operators can be reused when compatible. An IngressClass alone does not prove that a reachable load balancer exists.

## Preliminary compute recommendation

There is **no certified hardware minimum in the installer code**. For a preliminary proof of concept with modest traffic and all dependencies in-cluster, plan **three workers with 4 vCPU and 16 GiB RAM each**. This is not a contractual minimum, a performance promise, or an HA configuration. Kubernetes system workloads, all enabled Platform components, database choices, rollout headroom, node failure, and actual telemetry rates can require substantially more capacity.

If PostgreSQL is managed outside the cluster, its capacity is additional and must be sized independently. Even with three workers, one ClickHouse replica and one Keeper replica are still single points of failure. Production sizing requires measured ingestion, concurrent queries, retention, compression, burst behavior, stream replication, and recovery objectives. Measure CPU, memory, disk utilization/latency, queue depth, and ingestion/query throughput during acceptance and increase requests or capacity before saturation.

## Initial resource defaults

These are dependency defaults, **not the total Platform resource budget**. Requests reserve scheduling capacity; limits are not guaranteed available resources. CPU/memory figures are per replica.

| Component | Replicas | CPU request / limit | Memory request / limit | Requested PVC capacity |
| --- | --- | --- | --- | --- |
| NATS / JetStream | 3 | `100m` / `1` | `256Mi` / `2Gi` | `50Gi` each, `150Gi` total |
| ClickHouse | 1 | `1` / `4` | `2Gi` / `8Gi` | `100Gi` |
| Keeper | 1 | `100m` / `500m` | `256Mi` / `512Mi` | `10Gi` |

NATS also starts with `50Gi` stream capacity and a Go memory limit of `1600MiB`. Do not equate a stream capacity setting with guaranteed usable disk after filesystem and operational overhead.

The initial sum is **3 × 50Gi + 100Gi + 10Gi = 260Gi of logical requested PVC capacity only**. It excludes PostgreSQL, filesystem/database overhead, provider replication overhead, backups, snapshots, additional replicas, other Platform volumes, and free-space headroom. It is neither usable telemetry retention nor a complete physical-storage bill. Additional stream replicas consume additional storage within the topology; raising retention without sizing disk and write throughput can exhaust capacity.

## Durable storage and scheduling

Select the StorageClass explicitly. The ClickHouse wizard proposes the default class or a `WaitForFirstConsumer` class if no default exists, rejects legacy in-tree provisioners, and expects registered CSI or supported modern dynamic provisioners. Node-local storage can suit disposable development; it is not a substitute for durable production storage.

Plan volume expansion, reclaim policy, backups, recovery, IOPS/throughput, and zone affinity. `WaitForFirstConsumer` helps initial scheduling; it does not relocate existing volumes. Selectors must match Ready nodes and the zones of **all** existing PVs. Reserve headroom for drains and rolling updates.

For durable dependencies, prefer an approved stable node pool, commonly On-Demand. Spot interruption can disrupt quorum, ingestion, or recovery; a selector is not a durability policy. The installer does not silently choose Spot or On-Demand. If using interruptible capacity, explicitly engineer placement, disruption budgets, replica distribution, and recovery. Three NATS replicas do not by themselves prove cross-zone placement or end-to-end HA.

## Network and service dependencies

| Path | Required access |
| --- | --- |
| Workstation → Kubernetes | API endpoint and authentication/authorization refresh |
| Workstation → PostgreSQL | Private DNS/routing/VPN or approved tunnel for migrations; actual database port, commonly `5432` |
| Pods → PostgreSQL | Separate runtime reachability; a workstation tunnel does not provide Pod connectivity |
| Platform consumers → ClickHouse | Native protocol endpoint, commonly `9000` or TLS `9440`, as configured by your provider |
| Pods → NATS | Approved in-cluster service access and policies for JetStream consumers/producers |
| Workstation/cluster → dependencies | Approved Git/chart/operator sources and image registries; this is not a complete air-gapped workflow |
| Browsers → Portal/Admin | DNS, ingress/load balancer, trusted HTTPS, and identity-provider callbacks |
| Workloads → identity/email services | Provider endpoints and, for invitations, authorized cloud APIs and working email delivery |

Do not expose PostgreSQL, ClickHouse, or NATS publicly just to complete setup. Apply private routes, firewall/security-group rules and NetworkPolicies appropriate to the selected ports and workloads. Plan HTTPS for user-facing production login and verified TLS, optionally mTLS, for database connections. Continue with [preparation](../preparation/).