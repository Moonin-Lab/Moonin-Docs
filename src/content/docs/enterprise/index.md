---
title: "Enterprise Installer"
description: "Plan, install, secure, and operate a customer-managed Moonin Enterprise platform on Kubernetes."
sidebar:
  order: 1
---

Moonin Enterprise Installer guides your operator through deploying the Moonin platform into your Kubernetes environment. You need `moonin-installer` in your workstation's `PATH` and a signed customer license provided through Enterprise onboarding. This section covers the platform itself, not just the agents installed in monitored clusters.

## Get the latest installer

[Open the Moonin Installer package on GitHub Packages](https://github.com/Moonin-Lab/Moonin-Installer/pkgs/container/moonin-installer).

This permanent link lists published versions without requiring documentation updates. The package contains Linux, macOS and Windows archives for `amd64` and `arm64`, plus `SHA256SUMS`. It is an OCI file package, not an application container.

### Download for your operating system

Install [ORAS CLI](https://oras.land/docs/installation/), then run the command for your system. Each option downloads only its archive and `SHA256SUMS`, not the other platforms. These are OCI downloads, not direct browser links to executable files.

| Operating system | Architecture | Download command |
| --- | --- | --- |
| Linux | Intel / AMD x86-64 | `oras pull ghcr.io/moonin-lab/moonin-installer:latest-linux-amd64 --output installer-download` |
| Linux | ARM64 | `oras pull ghcr.io/moonin-lab/moonin-installer:latest-linux-arm64 --output installer-download` |
| macOS | Intel | `oras pull ghcr.io/moonin-lab/moonin-installer:latest-darwin-amd64 --output installer-download` |
| macOS | Apple Silicon | `oras pull ghcr.io/moonin-lab/moonin-installer:latest-darwin-arm64 --output installer-download` |
| Windows | Intel / AMD x86-64 | `oras pull ghcr.io/moonin-lab/moonin-installer:latest-windows-amd64 --output installer-download` |
| Windows | ARM64 | `oras pull ghcr.io/moonin-lab/moonin-installer:latest-windows-arm64 --output installer-download` |

After downloading, verify the archive on macOS/Linux:

```bash
cd installer-download
shasum -a 256 -c SHA256SUMS
```

The release pipeline updates the six `latest-OS-ARCH` aliases after verifying all platform packages, including prereleases such as `rc`. These aliases become available with the first release using that pipeline update; until then, select a published version tag on the package page. The combined `latest` package remains available for downloading all six archives. On Linux, you can also use `sha256sum --check SHA256SUMS`.

On Windows, verify and extract using PowerShell:

```powershell
Set-Location installer-download
$checksum = (Get-Content SHA256SUMS -Raw).Trim() -split '\s+', 2
if ((Get-FileHash -LiteralPath $checksum[1] -Algorithm SHA256).Hash -ne $checksum[0]) {
  throw 'Checksum mismatch'
}
Expand-Archive -LiteralPath $checksum[1] -DestinationPath .\bin
.\bin\moonin-installer.exe version
```

On Linux/macOS, after a successful checksum verification, extract the downloaded archive with `tar -xzf ARCHIVE.tar.gz`, replacing `ARCHIVE.tar.gz` with its actual filename. Run `./moonin-installer version` before installing it in your `PATH`.

Extract only the archive matching your operating system and architecture, and place its executable in your `PATH`. No Docker or source repository access is required. Public packages allow anonymous downloads; private packages require an authorized GitHub account and ORAS login. Do not place access tokens in this documentation or command arguments.

`latest` can change and does not mean the latest stable release. For production, use an approved version tag or digest instead, record it, and verify the extracted binary with `moonin-installer version`. Checksums verify integrity against the manifest, not independent authenticity of the publisher.

## Installation journey

1. Check [requirements](requirements/): workstation tools, Kubernetes compatibility, storage, permissions, and preliminary capacity planning.
2. Complete [preparation](preparation/): license, private database endpoints, certificates, identity applications, and the initial organization's administrator.
3. Follow [installation](installation/): prepare ClickHouse, migrate PostgreSQL, create the first organization, then complete the nine Platform stages.
4. Validate [authentication](authentication/): separate Portal and Admin sessions, identity callbacks, and optional Cognito invitations.
5. Use [operations](operations/) for acceptance checks, license renewal, configuration repairs, upgrades, diagnosis, and controlled removal.

Examples use Bash syntax. Linux, macOS, and Windows workstation variants support `amd64` and `arm64`; use the variant supplied for your OS and architecture. On Windows, adapt shell syntax, quoting, environment-variable handling, and paths for PowerShell. Workstation architecture does not guarantee that every platform image supports your Kubernetes nodes.

```bash
moonin-installer version
moonin-installer --help
moonin-installer platform install --help
```

Record the Installer version separately from the Platform chart version and its application/image versions. They are not interchangeable. Consult the supplied command's help for flags supported by that version.

## Deployment boundaries

| Layer | Responsibility |
| --- | --- |
| Customer infrastructure | Kubernetes, private networking, PostgreSQL, DNS, certificates, durable storage, approved workload identities, backups, and identity-provider applications |
| Installer-guided dependencies | Reuse or configure ingress and NATS; optionally install ClickHouse, Keeper, cert-manager, and the ClickHouse Operator |
| Platform configuration | License and connection Secrets, Portal/Admin authentication, placement, chart version, exposure, and reviewed Helm deployment |
| Post-install operation | Functional testing, monitoring, retention sizing, recovery exercises, account governance, and controlled maintenance |

The installer does not create your cluster, PostgreSQL/RDS, VPC, public certificates, DNS records, Cognito pools, Google identity applications, or Entra applications. On EKS, a separately confirmed storage-assistance path can create or reuse IAM, Pod Identity, EBS CSI, and StorageClass resources. Treat that as an infrastructure change requiring approval, not an implicit prerequisite fix.

The dependency path is:

```text
Workstation + authorized Kubernetes context
  -> durable storage + network + PostgreSQL + identity + customer license
  -> external ClickHouse OR ClickHouse installation wizard
  -> PostgreSQL migrations + first organization
  -> nine-stage Platform wizard
  -> HTTPS + authentication + ingestion/query acceptance checks
```

For an external ClickHouse service, skip `clickhouse install`, not the connection configuration. Platform's ClickHouse connection stage does not install the analytics engine or replace PostgreSQL migrations. Agent onboarding in monitored clusters is a separate task after platform acceptance.

## Customer license and scope

A signed `customer` license enables the customer deployment according to its validity, features, and capacity. Billing Sync and AI Sync are SaaS-only synchronization services and remain disabled for customer licenses in both quick and customized installation. This does not mean that all other AI-related functionality is disabled; availability depends on the licensed features and configured services.

The installer is not a capacity certification or a high-availability design. In particular, its initial ClickHouse and Keeper topology has one replica of each. Review the resource tables and production design constraints in [requirements](requirements/) before approving a deployment.

## Safety model

Secrets are sensitive even when stored in Kubernetes. Apply namespace-aware RBAC, encryption at rest, controlled terminal access, and backup protection. Do not put passwords, connection strings containing credentials, signed licenses, or private keys in values files, command arguments, support tickets, or Git. Interactive text fields are not universally masked; do not record credential-entry sessions or enable shell tracing.

The complete installation is **not one transaction**. Earlier stages can modify Secrets or install dependencies before final review. Cancelling review does not undo those changes. Helm's atomic rollback covers its own failed operation, not earlier stages, external migrations, or later verification failures. See [installation](installation/) for the approval boundaries.

## Related documentation

- [Product architecture](../getting-started/architecture/)
- [Agent installation in monitored clusters](../getting-started/installation/)
- [Spanish Enterprise Installer documentation](../es/enterprise/)

The agent guide describes a different installation scope. Use endpoints and credentials approved for your Enterprise deployment rather than copying hosted-service settings into it.