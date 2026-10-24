---
title: "Preparation"
description: "Prepare the customer license, database security, identity applications, DNS, and deployment decisions."
sidebar:
  order: 3
---

Start after completing [requirements](../requirements/). Agree on an installation owner, infrastructure approver, database administrator, identity administrator, backup owner, and maintenance window. Keep non-secret decisions in your change record; store credentials only in approved secret-management systems.

## 1. Prepare the signed customer license

Obtain a valid signed `customer` license through enterprise onboarding. Prepare the complete JWS text for interactive entry, not a filename. Check customer identity, validity dates, licensed features, capacity, storage entitlement, and support terms. The installer verifies signature and expiration; it does not generate licenses.

Compute Units (CU) express the greater of aggregate declared CPU and memory divided by two, rounded up:

```text
CU = max(ceil(aggregate vCPU), ceil(aggregate RAM in decimal GB / 2))
Exact license fields:
CU = max(ceil(declared_vcpu_millicores / 1000), ceil(declared_memory_mb / 2000))
```

For example, declared capacity of 12 vCPU and 48 decimal GB RAM corresponds to `max(12, 24) = 24 CU`. Aggregate the capacity scope agreed in your license; do not silently substitute Kubernetes limits, allocatable capacity, or a per-node calculation. Decimal MB/GB in license fields are not Kubernetes MiB/GiB. The customer-license validation also expects included storage of `10 GB × CU`; entitlement is not a statement of provisioned PVC capacity or effective retention. Confirm the signed agreement and capacity scope with onboarding rather than editing claims.

Platform validates `moonin/moonin-license`, key `MOONIN_LICENSE`. You can install or renew it separately using `moonin-installer license install`; existing valid licenses can be reused during Platform installation. Do not place the JWS in arguments, values files, screenshots, or logs. Billing Sync and AI Sync stay disabled for `customer` licenses; do not enable SaaS synchronization to work around a license problem.

## 2. Reserve names, versions, and endpoints

| Decision | Preparation |
| --- | --- |
| Kubernetes context | Approved target context and permissions; confirm it immediately before writing |
| Platform chart | An actual published chart version tested with your dependency versions; record application/image versions separately |
| Namespace conventions | Platform defaults to `moonin`; ClickHouse to `moonin-clickhouse`; NATS to `nats` |
| User-facing DNS | For example `portal.example.com` and `admin.example.com`, with planned ingress, DNS ownership, and HTTPS certificates |
| PostgreSQL | Dedicated Moonin database, private endpoint, migration account and runtime account, CA bundle, optional mTLS |
| ClickHouse | External native-protocol service or a planned in-cluster stack; database/user permissions, TLS, capacity, and backups |
| NATS | Existing compatible service or approved three-replica JetStream installation, StorageClass, placement, and retention |
| Images | Registry reachability and an existing pull Secret if your selected images require one |

User-facing `example.com` names throughout this section are placeholders. Enter your approved hosts instead of accepting any suggested public URL in the wizard. Plan ingress class, private/public load balancer, base domain, TLS Secret, and certificate chain together. The installer neither creates DNS records nor issues public certificates.

## 3. Prepare PostgreSQL and transport security

Create a dedicated Moonin API database, **not** a Keycloak or unrelated application database. The migration account needs permissions for Moonin's tables, functions, triggers, and required extensions; confirm managed-service restrictions with the DBA. The runtime account can be separate and more restricted. Both accounts need the intended database and routing permissions, but migrations run from your workstation and runtime runs from Pods.

Prefer `verify-full` with a trusted CA and a database DNS name present in the certificate. For RDS, obtain the official RDS CA bundle from AWS through your approved process, verify its provenance and validity, and prepare its local PEM path. Do not substitute a random CA or disable hostname verification to hide an error.

| TLS selection | Meaning |
| --- | --- |
| `disable` | Unencrypted transport; unsuitable over untrusted networks |
| `require` | Requires encryption; not equivalent to explicit CA and hostname verification |
| `verify-ca` | Verifies the server certificate chain against the supplied CA |
| `verify-full` | Verifies the chain and the database hostname; preferred with correctly configured DNS and certificates |

The wizard derives its initial TLS choice from the connection URL. There is no universal safe default that replaces your review. Optional mTLS needs a client certificate and private key accepted by the database. Protect local private-key permissions and renewal procedures.

Migration connections use local CA/client-certificate paths. For runtime, the installer stores PEM **contents**, not workstation paths, in a namespace-scoped Secret:

| Default Secret | Key | Content |
| --- | --- | --- |
| `moonin/db-secret` | `DATABASE_URL` | Runtime connection URL |
| `moonin/db-secret` | `DATABASE_TLS_CA_PEM` | CA bundle when needed |
| `moonin/db-secret` | `DATABASE_TLS_CLIENT_CERT_PEM` | Optional mTLS certificate |
| `moonin/db-secret` | `DATABASE_TLS_CLIENT_KEY_PEM` | Optional mTLS private key |

A workstation connection using `localhost` through a tunnel must not be copied into runtime unchanged. Inside a Pod, `localhost` is that Pod. A tunnel can also break hostname verification; use an approved connection design that preserves the certificate identity, rather than weakening TLS. Custom Secret names must also match the chart references; a Secret in another namespace cannot be consumed directly by a Pod in `moonin`.

## 4. Prepare the first organization

The current CLI's initial-organization bootstrap requires Microsoft Entra ID details **even if Portal/Admin email/password authentication will use Cognito or Identity Platform**. These are separate configuration layers. Arrange the following before `migrate`:

| Input | Required preparation |
| --- | --- |
| Organization name and slug | Agreed display name and unique slug |
| Owner administrator email | Valid accountable administrator, for example `owner@example.com` |
| Primary domain | Usually the owner's email domain; verify ownership and intended organization boundary |
| Entra tenant ID | Existing tenant prepared by your identity administrator |
| Application/client ID | Existing application registration with approved settings |
| Client secret | The secret **value**, not its identifier; valid for the installation and renewal plan |
| Authority host | Normally `https://login.microsoftonline.com`; use the approved authority for your tenant/cloud |

The installer does not create the Entra application or prove a complete sign-in flow merely by saving this information. The client secret is not printed or saved locally by bootstrap, but **is persisted in PostgreSQL**. Protect the database and its backups accordingly. You may defer organization creation with `migrate up --skip-organization` and later run `bootstrap organization`, but this does not remove the current Entra input requirement.

## 5. Prepare Portal and Admin identities

Choose Identity Platform, Cognito, or both with one active email/password provider. Google social OAuth is independent and can coexist with either. Prepare provider applications, credentials, authorized domains, callbacks for both Portal and Admin, and tested email delivery. Nothing in the installer provisions those identity applications.

Use two application session secrets, distinct public URLs, and distinct cookie prefixes, even when provider credentials are reused. Review the complete key table, Google callback examples, optional Cognito TOTP behavior, and invitation role in [authentication](../authentication/).

For Cognito on EKS, arrange a workload IAM role for Admin invitations rather than static AWS credentials. Its permissions must be scoped to the intended user pool and its trust restricted to the Admin ServiceAccount. The operator's local AWS session is not passed to Pods.

## 6. Approve storage, recovery, and overrides

Agree on StorageClass, zone-compatible selectors, stable node pools, volume sizes, retention, and capacity headroom. The default single ClickHouse/Keeper topology is not HA. Confirm PostgreSQL, ClickHouse, and JetStream backup schedules, ownership, restore testing, and recovery objectives before accepting production traffic.

If supplying a values file, use an existing local file reviewed for the selected chart and containing **no secrets**. Explicit overrides take precedence over generated values, including settings affecting security, images, and enabled services. Do not use a values file to bypass the signed license's deployment mode.

Confirm access to dependency sources and registries, compatibility of existing controllers, and approval for any EKS CSI setup. Record resource ownership so that future removal does not delete shared infrastructure. Continue with [installation](../installation/).