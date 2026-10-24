---
title: "Operations and Troubleshooting"
description: "Validate, maintain, repair, upgrade, and safely remove Enterprise installations without exposing credentials."
sidebar:
  order: 6
---

Use these procedures after [installation](../installation/). Reconfirm the active Kubernetes context and approved maintenance window before any write. Read-only checks do not replace end-to-end acceptance, and a healthy release does not prove database recovery or sufficient capacity.

## Acceptance and ongoing health

Start with read-only Installer and Kubernetes status. Adapt namespaces and ClickHouse names if customized. For external ClickHouse use the provider's approved health checks instead of in-cluster status. `migrate status` needs a securely supplied database connection reachable from the workstation.

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

Review events locally before sharing; sanitize names and potentially sensitive messages. Do not dump Secrets or raw kubeconfig for diagnostics. Discover actual workload names rather than assuming deployment names for every chart version.

| Acceptance area | Evidence to obtain |
| --- | --- |
| Workloads and storage | Expected replicas Ready, no repeated restarts, PVCs Bound, correct zones/selectors, no scheduling or volume-attach errors |
| DNS/HTTPS | Portal/Admin real hosts resolve to the approved ingress and present trusted matching certificates |
| Authentication | Independent login/logout, owner access, organization boundaries, active providers, email verification and MFA as applicable |
| Invitations | Approved non-demo recipient gets the invitation and completes first-login/password/MFA setup |
| Database and analytics | Applied migration status, API runtime connectivity, successful analytics requests, no TLS/privilege failures |
| Telemetry | A controlled monitored workload sends current data that appears in the intended organization/project and can be queried |
| Capacity | Measured ingestion/query rates, latency, queue depth, disk growth, CPU/memory and remaining retention headroom |
| Recovery | Tested restore procedure for PostgreSQL, ClickHouse and JetStream, with accountable owners and recovery objectives |

The Platform wizard does not install agents into all monitored clusters. Coordinate separate [agent onboarding](../../getting-started/installation/) using Enterprise-approved endpoints and credentials, not hosted-service defaults. Confirm fresh timestamps and correct tenant boundaries rather than treating an old populated dashboard as evidence of current ingestion.

If metrics-server is available and you are authorized, these are additional read-only checks:

```bash
kubectl top nodes
kubectl -n moonin top pods
kubectl -n nats top pods
kubectl -n moonin-clickhouse top pods
```

Missing metrics-server does not itself mean Moonin installation failed. CPU/memory snapshots do not measure disk capacity, ingestion throughput, retention, or full analytics health; use approved storage/cloud metrics and application dashboards as well. Compare observations against requests/limits and expected traffic, not only the preliminary PoC recommendation.

## Renew or repair the license

```bash
moonin-installer license install
```

Paste the complete signed JWS interactively. The installer verifies signature, validity, customer/type and limits before applying `moonin/moonin-license`, key `MOONIN_LICENSE`. `license upgrade` is an alias. Invalid, altered, or expired licenses do not modify Kubernetes. Existing namespaces are reused; license renewal does not require uninstalling Platform.

After renewal, arrange a controlled restart/redeploy of consumers that load the license at startup, then verify readiness and licensed functionality. Updating the Secret does not guarantee a running process reloads it. Do not use a namespace deletion, database edit, or SaaS-service override to repair license validation. Keep the license text out of support evidence and shell arguments.

## Repair connections or authentication

| Need | Supported procedure | Follow-up |
| --- | --- | --- |
| Portal authentication | `moonin-installer portal configure` | Review URL/provider/cookie, then controlled consumer rollout |
| Admin authentication | `moonin-installer platform auth admin configure` | Review reuse and independent session secret/cookie; configure workload invitation role |
| ClickHouse connection | `moonin-installer clickhouse connection` | Verify native protocol/TLS and runtime reachability; redeploy consumers if required |
| Runtime PostgreSQL Secret / full prerequisites | Rerun the reviewed `platform install` flow, or use the interactive `migrate` wizard's runtime Secret stage | Review migration action carefully; preserve data and confirm runtime TLS/account |
| Missing initial organization | `moonin-installer bootstrap organization` with securely supplied `DATABASE_URL` | Only when none exists and migrations are applied; prepare mandatory Entra inputs |

Authentication repair commands do not update Helm or restart Pods. For `envFrom` consumers, newly created Pods are required to pick up new environment values. First discover workloads with `kubectl -n moonin get deployments,statefulsets`, then use your approved rollout/redeploy process for the actual consumers, monitor readiness, and retest. Rotate application session secrets only when intended because sessions are invalidated. Changing Portal does not automatically sync Admin.

Do not repair user access or schema state with manual SQL writes. If an organization already exists, use Admin's supported organization/user flows. Repeated initial bootstrap is not an account-recovery mechanism.

## Controlled Platform upgrade

1. Record Installer version, current chart/appVersion, actual images, non-secret explicit overrides, dependency versions, and resource ownership.
2. Select an actual published target chart; review compatibility, migration requirements, and changes with your support/change process. Validate in non-production first.
3. Back up PostgreSQL, ClickHouse, and JetStream and verify restore. Helm rollback does not restore data or automatically reverse separately executed migrations.
4. Plan any required migrations in the approved order. `migrate status` reports state; do not use `down`/`reset` as generic upgrade recovery.
5. Run the chart upgrade with a reviewed target and, if needed, an existing secret-free values file.
6. Inspect the plan and any NATS prerequisite changes before accepting. Repeat all acceptance checks after completion.

```bash
moonin-installer platform upgrade --help
moonin-installer platform upgrade \
  --version APPROVED_CHART_VERSION \
  --values /absolute/path/enterprise-values.yaml
moonin-installer platform status
```

Replace placeholders or omit `--values` if you have no overrides. The Installer version, chart version and application version remain separate. This command changes the chart; it is not an auto-update of the workstation command.

`platform upgrade` does not repeat the entire authentication/Secret wizard, but can request confirmed NATS changes before bootstrap. Values are resolved in this ascending priority: new chart defaults, previous explicit configuration, generated values, then `--values`. Default-only images can advance while explicit pins remain. Review the resulting images rather than assuming every component updates uniformly. Rerun `platform install` when you need its prerequisite review.

Helm's atomic behavior covers its failed install/upgrade, not prior Secret/dependency changes, external migrations, or a verification error after Helm succeeds. The installer checks rendered/live workload image declarations, including init containers; later mismatches stop success but do not trigger an automatic rollback. Inspect the actual deployment before retrying.

## NATS placement and repair

For NATS chart `2.14.2`, the valid selector path is `podTemplate.merge.spec.nodeSelector`, not legacy `podTemplate.merge.nodeSelector`. A valid `spec` selector, including an empty one, is authoritative. The installer compares desired/effective placement against Ready nodes and PV zone affinity, and a confirmed repair removes the legacy path while preserving other overrides.

If desired placement does not cover all PV zones, recover suitable nodes or explicitly approve preserving compatible effective placement when offered. A reset is not a substitute for compatible nodes. Repair/reset questions default to **No**. Legacy reset paths can lose JetStream data; repaired values are saved before the reset and a failed Helm repair does not justify deleting volumes. External releases are inspected but not repaired/reset by this ownership-aware path.

## Controlled removal and ownership

Stop traffic, agree on retention, take verified backups, inventory consumers/shared dependencies, and confirm the context before removing anything. The Platform ownership ledger `moonin/moonin-platform-install-state` distinguishes `created`, `reused`, and `external`. Do not edit/delete it to force removal; without a ledger the installer refuses to guess.

```bash
moonin-installer platform uninstall
```

Only owned `created` resources are proposed for removal. Reused/external resources are preserved, and namespaces are kept by default. This does not delete PostgreSQL/RDS or external/independently installed ClickHouse. `--yes`, where supported, skips confirmation, not ownership checks; avoid it during a first reviewed removal.

**Destructive namespace option:** `platform uninstall --delete-created-namespaces` can also delete resources added later by other operators, **including PVCs**. Do not use it merely because a namespace remains. Inspect its current contents and backup/recovery plan before approval.

To remove only installer-owned NATS while normally retaining JetStream PVCs:

```bash
moonin-installer platform nats uninstall
```

Its namespace-deletion flag is singular: `--delete-created-namespace`, also potentially destructive. `platform nats adopt` is for verified legacy installer-owned resources only, never permission to appropriate a shared release. Neither removal nor adoption automatically proves data ownership.

ClickHouse has its own lifecycle:

```bash
moonin-installer clickhouse uninstall
```

Confirm the original namespace/cluster, using matching supported flags if customized. It removes selected ClickHouse/Keeper resources and their password Secret while **retaining PVCs by default**. Preserve credentials securely before removal so retained data can be recovered. `--delete-data` permanently removes selected PVCs; selection uses cluster-name prefixes, so inspect potential prefix collisions first.

`--remove-operator` and `--remove-cert-manager` are independent opt-ins. Only recorded installer-owned dependencies that pass shared-use checks can be removed; preexisting/shared namespaces, CRDs and installations are not automatically deleted. EKS resources created by storage assistance are removed only after checks for PVCs, EBS PVs and other Pod Identity associations. Use `--keep-eks-storage` to preserve them deliberately. Legacy resources without ownership records are preserved; `clickhouse adopt-eks-storage` is only for independently verified installer-owned legacy storage, not a way around shared-resource review.

### Database rollback is a separate destructive action

`migrate down` reverts the latest migration; the direct action does **not** ask the interactive wizard's confirmation. `migrate reset --confirm-reset` reverts every migration and can remove schema objects and data. Interactive `down`/`reset` confirmations default to **No**, but that does not make direct commands safe. Neither is part of normal removal, connectivity repair, or a routine retry. Execute only under a DBA-approved recovery plan with tested backups.

## Troubleshooting

| Symptom | Likely boundary and next action |
| --- | --- |
| `exec format error` | If the workstation cannot start the command, verify its OS/CPU variant against the workstation. If a Pod/container reports it, inspect that image's supported node architecture; a multiarch Installer does not make every workload image multiarch. Do not disable security or rebuild dependencies as a diagnosis shortcut |
| `Unauthorized` from Kubernetes on EKS | Check context and renew the operator's AWS/SSO session using your approved access process, then retry a read-only query. This is different from an application `CrashLoopBackOff`; refreshing operator credentials does not repair a crashing Pod |
| Root command says `not implemented` | Use `platform install/status/upgrade/uninstall`, not similarly named root placeholders. `init` produces a template only; no implemented `apply -f` or `platform install --config` consumes it |
| Missing executable/dependency | Check `PATH`, `kubectl`, Git and Helm versions. ClickHouse needs Helm CLI even though Platform integrates Helm |
| License rejected | Check full JWS, validity, compatible signature, declared capacity and clock. Obtain corrected signed license through onboarding; do not edit claims |
| PostgreSQL timeout | Check private DNS, VPN/routing, port, security groups and Pod network separately from workstation connectivity |
| RDS/TLS hostname or CA error | Use the official current CA bundle, `verify-full` and matching database DNS. Verify local paths for migrations and PEM contents in the runtime Secret through approved tooling; do not print private keys or disable verification to hide the error |
| Migration privilege error | Ask DBA to verify account/database and required object/extension privileges; `reset` is not a privilege repair |
| ClickHouse connection fails | Verify native endpoint/port, secure scheme, credential encoding, user/database permissions, TLS and runtime reachability |
| Admin session fails / missing `NEXTAUTH_SECRET` | Run Admin authentication repair, ensure its independent secret, correct Secret reference/namespace and explicit `moonin-admin` prefix, then restart/redeploy actual `envFrom` consumers |
| Wrong login redirect | Compare public URL, provider callback/origins, DNS, ingress and TLS for both applications |
| Cognito MFA/invitation fails | Review non-demo enrollment and pool TOTP setup; for invitations check exact IRSA subject/audience, pool-scoped actions, ServiceAccount annotation, template placeholders and email delivery |
| PVC Pending / NATS not Ready | Check CSI, StorageClass, capacity, Ready nodes, selectors, PV affinity and zones. Recover compatible nodes before considering destructive resets |
| ImagePullBackOff | Check image/tag availability, registry network access and actual pull Secret references; do not invent registry credentials |
| Post-Helm image mismatch | Inspect workload state and effective overrides; verification failure does not automatically roll back a successful Helm operation |
| Uninstall keeps resources | Inspect ownership and shared use; preservation can be expected behavior, not a failed deletion |

## Safe support evidence and command reference

Supply Installer/chart/application versions, OS/architecture, affected stage, sanitized error, resource readiness and relevant timestamps. Do not attach credential-bearing DSNs, JWS, `.env` files, raw kubeconfig, Secret manifests, private keys, database dumps, or unreviewed logs. Use narrowly scoped, redacted evidence rather than exporting the entire cluster configuration.

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

`--no-color` is global and only disables ANSI styling. `--yes` is command-specific, not a global unattended mode. The supplied command's help is the flag reference for your installed version. Return to the [Enterprise overview](../) or [authentication](../authentication/) for the relevant workflow.