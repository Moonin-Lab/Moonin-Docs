# Product Overview

Moonin combines change tracking, cluster inventory and operational governance for Kubernetes environments. The platform is organized around the idea that teams should be able to answer three questions quickly:

1. What changed?
2. What is affected right now?
3. Which automated policy or response should happen next?

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
| `app.moonin.app` | Main engineering workspace for dashboards, workloads, revisions, errors and policies |
| `app-admin.moonin.app` | Administration console for organizations, projects, clusters and notification channels |
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
