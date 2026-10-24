---
title: "Installation"
description: "Install ClickHouse, migrate PostgreSQL, bootstrap the first organization, and complete all nine Platform stages."
sidebar:
  order: 4
---

Complete [requirements](../requirements/) and [preparation](../preparation/) first. The CLI currently asks questions in English. Quoted labels below identify its prompts; explanations describe what to choose. Defaults can depend on existing resources and your connection URL: read the displayed choice rather than pressing Enter throughout.

## 1. Confirm the target

```bash
moonin-installer version
moonin-installer platform install --help
kubectl config current-context
kubectl get nodes
kubectl get storageclass
```

Confirm the approved context, Ready nodes, storage, private database reachability, identity credentials, and maintenance window. All examples use the onboarding-provided command in `PATH`. They use Bash syntax; adapt for PowerShell. Do not enable terminal recording or shell tracing while entering credentials.

## 2. Prepare ClickHouse before migrations

### Option A: external analytics service

Have your database administrator prepare a database, user, native-protocol endpoint, TLS settings, and network access for Platform consumers. Do not run the installation wizard. Configure its connection either now or in Platform stage 5:

```bash
moonin-installer clickhouse connection
```

The supported URI shape is `clickhouse://` for the native protocol or `clickhouses://` for secure native connections, with provider-appropriate port and database. Use percent-encoding for reserved characters in credentials. Do not use an HTTP endpoint by analogy. Enter sensitive DSNs interactively in a protected terminal; syntactic validation does not prove connectivity or privileges.

### Option B: initial in-cluster stack

```bash
moonin-installer clickhouse install
```

Review each decision in this wizard before starting Platform:

| Question or decision | Initial value / operator action |
| --- | --- |
| Namespace and cluster name | `moonin-clickhouse` and `clickhouse`; record any changes for later status/removal |
| StorageClass | Proposed default class, otherwise an eligible `WaitForFirstConsumer` class; select a supported durable CSI class explicitly |
| ClickHouse data volume | `100Gi`; size for measured ingestion and retention |
| Keeper volume | `10Gi`; include coordination recovery in your design |
| CPU/memory | ClickHouse request `1`/`2Gi`, limit `4`/`8Gi`; Keeper request `100m`/`256Mi`, limit `500m`/`512Mi` |
| Node selector | Optional `key=value`; blank leaves scheduling to Kubernetes. A selected label must match Ready nodes and volume zones |
| Password | Existing `clickhouse-password` key `password` is reused; otherwise enter and confirm the password, hidden in a compatible terminal |
| Dependencies | Reuse compatible cert-manager/Operator installations, including those in other namespaces; review approval before creating missing dependencies |
| Platform connection after installation | Offered with **Yes** as default; creates the connection Secret for Platform |

The initial topology is one ClickHouse and one Keeper replica, **not HA**, with a `20m` timeout. The installer uses cert-manager `v1.20.4` when it needs to install it; the Operator manifest source follows `releases/latest` rather than a pinned version. Record the actual deployed dependency versions and assess their Kubernetes compatibility before production use.

On EKS without EBS CSI, `"Enable Amazon EBS CSI now through AWS"` proposes **Yes** but requires explicit acceptance and an authorized AWS identity. This path can configure a dedicated role, Pod Identity Agent, EBS CSI, and `moonin-ebs-gp3`. It prefers `AmazonEBSCSIDriverPolicyV2`; a fallback to the broader `AmazonEBSCSIDriverPolicy` is warned about. Review IAM scope before agreeing. Existing shared dependencies are reused, not automatically owned. On GKE/AKS, prepare the corresponding CSI driver through your infrastructure procedure.

If avoiding detection ambiguity, supported flags include:

```bash
moonin-installer clickhouse install \
  --namespace moonin-clickhouse \
  --cluster-name clickhouse \
  --storage-class APPROVED_STORAGE_CLASS \
  --data-size 100Gi \
  --keeper-size 10Gi
moonin-installer clickhouse status
```

Replace `APPROVED_STORAGE_CLASS`. For customized names, include the same `--namespace` and `--cluster-name` in status commands. Do not rerun solely to rotate the password: an existing password Secret is reused.

## 3. Migrate the dedicated PostgreSQL database

```bash
moonin-installer migrate
```

The wizard runs from the workstation, not a Pod. It does not load environment files automatically. It can use a securely injected `DATABASE_URL`; the supported `--database-url` flag takes precedence but is unsuitable for secrets in shell history/process arguments. Never target another application's database.

| Step / English prompt | Explanation and default |
| --- | --- |
| 1. `"PostgreSQL connection"` | Enter the dedicated Moonin connection. `"Use the supplied database URL"` defaults to **Yes** if one was supplied |
| 2. `"PostgreSQL transport security"` / `"TLS mode"` | Review the mode derived from the URL. Prefer `verify-full`; provide `"CA bundle PEM file path"` and optional mTLS files as requested |
| 3. `"Migration action"` | Default `up` applies pending migrations. Interactive rollback confirmations for `down` and `reset` default to **No** |
| 4. `"Execute"` | Applies the chosen action. After `up`, can offer first-organization creation if none exists |
| 5. `"Moonin API database Secret"` | Offers to create/update the runtime Secret, default **Yes**; reusing the migration connection defaults to **Yes**. Choose **No** when runtime uses another account/endpoint |

The normal runtime destination is `moonin/db-secret`. Updating an existing database Secret defaults to **No**; applying the reviewed Secret defaults to **Yes**. Confirm Pod-reachable DNS, not workstation `localhost`, and runtime PEM contents. See [TLS modes and Secret keys](../preparation/) before accepting. If using a custom Secret, also align `moonin-api.databaseSecret.existingSecret`; Platform's normal flow expects `moonin/db-secret`.

The embedded PostgreSQL migrations record applied versions in `goose_db_version`, including routing metadata for ClickHouse. They do not create the analytics engine's data tables. A connection Secret, successful Helm release, or bootstrap hook alone is not independent proof that the expected PostgreSQL schema is applied.

### Create the first organization

After `up`, `"Create the first organization now"` defaults to **Yes** only when no organization exists. Enter organization name, slug, owner email, primary domain (proposed from the email), Entra tenant ID, application/client ID, **client secret value**, and authority host (normally `https://login.microsoftonline.com`). Entra inputs are mandatory in the current bootstrap even if the global password provider is Cognito or Identity Platform.

Review all non-secret details. `"Create the first organization"` defaults to **No** before writing. Confirmation creates the organization, domain, initial administrator, and Entra configuration. The client secret is persisted in PostgreSQL, so protect the database/backups. This neither registers an Entra application nor verifies browser login end to end.

To defer bootstrap or separate automation, with `DATABASE_URL` already supplied securely and TLS parameters already included:

```bash
moonin-installer migrate status
moonin-installer migrate up --skip-organization
moonin-installer bootstrap organization
```

Direct migration actions **do not run the TLS wizard or create the runtime Secret**. Include `sslmode=verify-full`, `sslrootcert` and, for mTLS, `sslcert`/`sslkey` paths in the injected connection as appropriate. Use the interactive migration flow when you need runtime Secret preparation. Explicit bootstrap requires the schema and refuses if an organization already exists; create subsequent organizations in Admin. Do not repair bootstrap with manual SQL writes.

## 4. Run the nine Platform stages

```bash
moonin-installer platform install
```

For a reproducible production change, pin an actual published chart version. An optional reviewed values file must already exist, match that chart, and contain no secrets:

```bash
moonin-installer platform install \
  --version APPROVED_CHART_VERSION \
  --values /absolute/path/enterprise-values.yaml
```

Replace both placeholders. Values overrides take precedence over generated settings; review images, security, exposure, and enabled services in the final plan. No global `--yes` makes this wizard unattended.

### Stage 1 of 9: Signed Moonin license

Validates `moonin/moonin-license`, key `MOONIN_LICENSE`, including signature and expiration. Reusing a valid existing license defaults to **Yes**. If missing or invalid, paste the complete signed JWS in the protected prompt. Review customer, type, validity, features, and limits; the installer does not generate a license or print its complete text.

### Stage 2 of 9: Ingress controller

Review discovered IngressClasses, controllers, and default class. Reuse your approved ALB, NGINX, GCE, Traefik, or other compatible controller, or approve installing Traefik `39.0.6` in `traefik-v2`. Review private/public load-balancer decisions on EKS. A class is not proof of external reachability. Platform ingress publication, DNS, and TLS are separate decisions later; DNS and public certificates are not created here.

### Stage 3 of 9: NATS and JetStream

Reuse an existing release or approve official chart `nats/nats` `2.14.2`. New defaults are namespace `nats`, three replicas, `50Gi` PVC per replica, `50Gi` stream capacity, CPU request/limit `100m`/`1`, memory `256Mi`/`2Gi`, and Go memory limit `1600MiB`.

Capacity customization defaults to **No**. Pinning a new installation to a node label defaults to **No**. Select StorageClass explicitly; customize odd replica counts, volumes, resources, or selector when justified. Review Ready nodes and all existing PV zones. Neither Spot nor On-Demand is selected silently. NATS configuration occurs **before** the quick/custom Platform choice.

An external release is preserved. The installer records ownership of its new release progressively to support resuming. Reuse can propose preserving an existing selector. Repair/reset prompts default to **No**: resets lose data and cannot fix missing compatible nodes. Diagnose placement before accepting a destructive remedy.

### Stage 4 of 9: Moonin API PostgreSQL Secret

Looks for `moonin/db-secret` key `DATABASE_URL`; reusing a usable existing connection defaults to **Yes**. Otherwise configure runtime connection and TLS/mTLS. Ensure Pod reachability and correct namespace. Presence of the key does not validate connectivity, privileges, or schema. This stage configures the Secret; it does not replace local `migrate`.

### Stage 5 of 9: ClickHouse analytics connection

Detects a `ClickHouseCluster` or accepts an external native-protocol URI. Stores `moonin/moonin-clickhouse-connection`, key `CLICKHOUSE_DSN`. A valid DSN is required to continue, but syntax is not a connectivity/permissions test. This stage **does not install ClickHouse**. Repair the connection independently with `moonin-installer clickhouse connection` if needed.

### Stage 6 of 9: Moonin Portal authentication Secret

Creates/updates `moonin/moonin-front-secret`. `"Generate a secure NEXTAUTH session secret"` is offered when missing; existing settings can be kept. Set `"Portal public URL"` to your approved URL, for example `https://portal.example.com`, and `"Cookie prefix"` to `moonin-portal`.

Configure email/password provider and optional Google OAuth. New Google social OAuth defaults to disabled; `Keep current` preserves existing settings rather than removing them. Verify provider credentials, active selection, and callback URLs using [authentication](../authentication/). Do not accept a suggested host that is not yours.

### Stage 7 of 9: Admin UI authentication and internal service credentials

Creates/updates `moonin/moonin-admin-ui-secret`. `"Reuse shared sign-in provider settings from Moonin Portal"` defaults to **Yes**, synchronizing provider keys, reCAPTCHA, and email auto-verification, **not sessions**. Generate/retain an independent Admin `NEXTAUTH_SECRET`, set `https://admin.example.com`, and explicitly enter cookie prefix `moonin-admin`. The shared cookie chooser may propose `moonin-portal` on a new Admin Secret: override it.

For active Cognito, review the detected/requested Admin invitation IAM role and workload trust. Local AWS credentials do not authorize Pods. Missing internal credentials are generated for `moonin-ai-delegation` key `secret` and `moonin-chatbot` key `gateway-secret`; existing values are reused and rotation needs confirmation. These internal credentials are distinct from SaaS-only AI Sync.

### Stage 8 of 9: Platform version and exposure

`"Use the recommended quick installation flow"` defaults to **Yes** after prerequisite configuration. Without `--version`, quick flow selects the latest published chart; customized flow asks for a version, with empty input selecting latest. Pin a tested version for production. Chart version and appVersion are displayed separately.

Both paths review placement and exposure. Quick flow uses an existing `ghcr-secret`; customized flow asks about reuse, default **Yes**. No missing pull Secret is referenced or invented. With a `customer` license, Billing Sync and AI Sync remain disabled in either path.

For an existing release, upgrading to a newer version or reconciling the same version defaults to **Yes**; downgrade or incomparable versions default to **No**. A release owned elsewhere needs update confirmation and does not become eligible for removal by the installer.

Choose whether to publish ingress, its class, base domain, and TLS. Reuse a TLS Secret or create one from local PEM certificate/chain and private-key files; interactive paths support Tab completion. HTTP is an explicit option to avoid a broken HTTPS configuration, **not a recommendation for production login**. Arrange DNS, certificates and identity callbacks yourself.

### Stage 9 of 9: Review and deploy

Review target, chart/application versions, images, placement, ingress, TLS, service enablement, overrides, and proposed changes before confirming. A Helm dry-run avoids printing Secrets. Helm waits for readiness and uses atomic rollback for a failed Helm operation.

Earlier Secret/dependency changes and PostgreSQL migrations are outside that rollback. After Helm, the installer checks chart and declared images in rendered resources and live workload templates, including init containers. A failure/mismatch at this later check stops success reporting but **does not automatically roll back**. Inspect state before retrying. This comparison is not proof of every running image's effective digest.

Ownership is progressively recorded in `moonin/moonin-platform-install-state` as `created`, `reused`, or `external`, without passwords, JWS, or DSNs. Do not delete or edit it to force ownership or removal. Final cancellation is not a promise that Kubernetes is unchanged.

## 5. Accept the deployment

```bash
moonin-installer platform status
moonin-installer clickhouse status
moonin-installer migrate status
kubectl -n moonin get pods,deployments,statefulsets,services,ingress,pvc
kubectl -n nats get pods,pvc
```

Skip in-cluster ClickHouse status for an external service; use its approved health checks instead. Migration status requires workstation database access. Validate DNS/HTTPS, independent Portal/Admin login and logout, owner permissions, invitations/email, PostgreSQL and analytics access, and real ingestion/query behavior. A Helm `deployed` result is not acceptance. Continue with [authentication](../authentication/) and the [operations acceptance checklist](../operations/).