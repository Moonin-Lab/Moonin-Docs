---
title: "Enterprise Installer"
description: "Plan, install, secure, and operate a customer-managed Moonin Enterprise platform on Kubernetes."
sidebar:
  order: 1
---

Moonin Enterprise Installer guides your operator through deploying the Moonin platform into your Kubernetes environment. You need `moonin-installer` in your workstation's `PATH` and a signed customer license provided through Enterprise onboarding. This section covers the platform itself, not just the agents installed in monitored clusters.

## Get the latest installer

[Open Moonin Installer public releases](https://github.com/Moonin-Lab/Moonin-Installer-Releases/releases).

This is the only public distribution channel. The source repository remains private. Each release contains Linux, macOS and Windows archives for `amd64` and `arm64`, plus `SHA256SUMS` and `RELEASE.txt`.

### Download for your operating system

Download directly in your browser, without authentication or access to the private source repository:

| Operating system | Intel / AMD x86-64 | ARM64 |
| --- | --- | --- |
| Linux | [Download Linux x86-64](https://github.com/Moonin-Lab/Moonin-Installer-Releases/releases/download/preview/moonin-installer_linux_amd64.tar.gz) | [Download Linux ARM64](https://github.com/Moonin-Lab/Moonin-Installer-Releases/releases/download/preview/moonin-installer_linux_arm64.tar.gz) |
| macOS | [Download macOS Intel](https://github.com/Moonin-Lab/Moonin-Installer-Releases/releases/download/preview/moonin-installer_darwin_amd64.tar.gz) | [Download macOS Apple Silicon](https://github.com/Moonin-Lab/Moonin-Installer-Releases/releases/download/preview/moonin-installer_darwin_arm64.tar.gz) |
| Windows | [Download Windows x86-64](https://github.com/Moonin-Lab/Moonin-Installer-Releases/releases/download/preview/moonin-installer_windows_amd64.zip) | [Download Windows ARM64](https://github.com/Moonin-Lab/Moonin-Installer-Releases/releases/download/preview/moonin-installer_windows_arm64.zip) |

These permanent URLs follow **preview**, including release candidates, not certified stable releases. [View the channel version](https://github.com/Moonin-Lab/Moonin-Installer-Releases/releases/tag/preview) and download [SHA256SUMS](https://github.com/Moonin-Lab/Moonin-Installer-Releases/releases/download/preview/SHA256SUMS). Compare your archive's SHA-256 with its exact entry before extracting it: use `shasum -a 256 ARCHIVE` on macOS, `sha256sum ARCHIVE` on Linux or `Get-FileHash -Algorithm SHA256 ARCHIVE` on Windows, replacing `ARCHIVE` with its filename. If it differs, discard the file and download both archive and manifest from the same versioned release.

For reproducible production downloads, choose an approved version from [all releases](https://github.com/Moonin-Lab/Moonin-Installer-Releases/releases). The separate `stable` channel is populated only by non-prerelease versions. Links become available after the first successful public-distribution pipeline run; creating the repository alone does not publish binaries.

### Verify, extract and add to PATH

Save your archive and `SHA256SUMS` in an `installer-download` directory. The manifest has six entries: verify only the exact filename you downloaded, not the entire manifest or its first line. On Linux/macOS, replace `ASSET` below with your archive's filename:

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

On Linux, you can replace `shasum -a 256 -c -` with `sha256sum -c -`. Stop if the entry is missing, duplicated or fails verification. Add `export PATH="$HOME/.local/bin:$PATH"` to your shell startup file (such as `~/.zshrc` or `~/.bashrc`) to persist it in new sessions.

On Windows, select your ZIP filename and run in PowerShell:

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

The Windows user `PATH` persists for new terminals; the last assignment also updates the current session. Extract only the archive for your operating system and architecture. No Docker or source repository access is required.

Both `preview` and `stable` can change. For production, record an approved versioned release tag and verify the extracted binary with `moonin-installer version`. Checksums verify integrity against the manifest, not independent authenticity of the publisher. After completing preparation, start the wizard with `moonin-installer platform install`.

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
- [Spanish Enterprise Installer documentation](https://docs.moonin.app/es/enterprise/)

The agent guide describes a different installation scope. Use endpoints and credentials approved for your Enterprise deployment rather than copying hosted-service settings into it.