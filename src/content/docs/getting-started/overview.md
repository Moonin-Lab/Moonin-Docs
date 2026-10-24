---
title: "Product Overview"
---

Moonin combines change tracking, cluster inventory and operational governance for Kubernetes environments. The platform is organized around the idea that teams should be able to answer three questions quickly:

1. What changed?
2. What is affected right now?
3. Which automated policy or response should happen next?

## SaaS and Enterprise

**SaaS** is the Moonin-hosted service: Moonin operates the platform and your team connects its monitored clusters under your subscription. The public application URLs below refer to this hosted service.

**Enterprise** runs in your organization's Kubernetes environment, with infrastructure, security, backups and upgrades operated by your team. It requires a **commercial, signed Enterprise customer license**. Contact Moonin Sales through your account representative or the official Moonin website to agree on capacity, features, validity and support and obtain your license before installation. Downloading the CLI does not grant an Enterprise license.

See [Enterprise deployment and licensing](../../enterprise/) for the comparison, license lifecycle and installation guide. Enterprise uses your own approved application endpoints rather than the hosted URLs below.

## Core capabilities

### Change intelligence

- Deployment and revision history
- Image tracking across clusters
- Helm release metadata for Helm-managed workloads
- Correlation between revisions and downstream errors

### Cluster and runtime inventory

- Cluster connectivity and cloud metadata heartbeats
- Namespace and deployment discovery
- Node snapshots with capacity, allocatable and conditions
- CronJob schedules, executions and failure context

### Operational governance

- Alert policies with scoped notification channels
- Event notification policies for cluster and deployment events
- Scaling rules with temporary HPA changes and automatic rollback
- Silencing and scheduling controls for channels and policies

## Main applications

| Application | Purpose |
|---|---|
| `portal.moonin.app` | Main engineering workspace for dashboards, workloads, revisions, errors and policies |
| `admin.moonin.app` | Administration console for organizations, projects, clusters and notification channels |
| `api-discover.moonin.app` | Control-plane API used by agents and the web apps |
| `api-scaling-rules.moonin.app` | Scaling rules control plane |
| `mcp.moonin.app` | Read-only MCP surface for AI tools and assistants |

## Recent platform areas reflected in these docs

- Overview dashboard with compact health and inventory signals
- Dedicated node inventory page with responsive, expandable rows
- CronJobs page with execution history and human-readable schedules
- Better AWS and GCP console deep links from the frontend
- Event notification policies and channel schedule UX
- Agent chart bundling Discovery Agent and Scaling Rules Agent

## Who uses Moonin

- Platform engineers managing multi-cluster environments
- SRE teams reviewing rollout impact and active incidents
- DevOps teams standardizing notifications and scaling behavior
- Application teams validating images, CronJobs and deployment history
