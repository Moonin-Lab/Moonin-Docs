---
title: "Architecture"
---

This document describes the high-level architecture of the Moonin platform. It focuses on the components that are currently visible in the product and in the public deployment flow.

## Platform overview

Moonin is built as a multi-tenant SaaS platform deployed on Kubernetes. Customers install the `moonin-agent` chart in their clusters. That chart currently bundles the Discovery Agent and the Scaling Rules Agent, both authenticated with the same cluster credentials secret.

```mermaid
graph TB
    subgraph "Your Infrastructure"
        K8S[Kubernetes Cluster]
        DISCOVERY[Discovery Agent]
        SCALING[Scaling Rules Agent]
        DISCOVERY -.->|Watches| K8S
        SCALING -.->|Reconciles HPAs| K8S
    end

    subgraph "Moonin Platform"
        API[Control Plane API]
        DI[Data Ingestion API]
        FRONT[Web Application]
        ADMIN[Admin Application]
        MCP[MCP Server]
        NOTIFIER[Notification Engine]
        SCALINGAPI[Scaling Rules API]
    end

    subgraph "External Integrations"
        GH[GitHub]
        ACD[ArgoCD]
        SLACK[Slack]
        TEAMS[Microsoft Teams]
        VOPS[VictorOps]
        AI[AI Tools / MCP Clients]
    end

    DISCOVERY -->|HTTPS + Token| API
    DISCOVERY -->|HTTPS + Token| DI
    SCALING -->|HTTPS + Token| SCALINGAPI
    FRONT -->|Proxy| API
    FRONT -->|Proxy| DI
    FRONT -->|Proxy| SCALINGAPI
    ADMIN -->|Proxy| API
    NOTIFIER --> SLACK
    NOTIFIER --> TEAMS
    NOTIFIER --> VOPS
    GH -.->|Webhooks| API
    ACD -.->|Webhooks| API
    MCP --> AI
    USERS[Users] -->|Browser| FRONT
    ADMINS[Administrators] -->|Browser| ADMIN
```

## Key components

### Discovery Agent

- watches Deployments, Jobs, CronJobs, HPAs, Namespaces, Services and related resources
- sends deployment metadata, node snapshots, CronJob inventory and cluster metadata
- uses leader election for high availability
- operates with configurable namespace and resource exclusions

### Scaling Rules Agent

- applies temporary HPA changes from scaling templates
- stores rollback state
- restores previous HPA values when templates expire or are disabled

### Control Plane API

The central API for deployment tracking, cluster management, organization administration, policy management, CronJob inventory and billing.

### Web Application

The main engineering workspace provides:

- overview dashboard
- clusters, nodes and namespace inventory
- deployments, revisions and image tracking
- CronJob schedules and execution history
- errors, notifications and policies

### Admin Application

The Admin Console manages:

- organizations and users
- projects and cluster onboarding
- notification channel creation and maintenance
- billing settings

### Notification Engine

A background worker that evaluates alert policies and event notification policies, then dispatches notifications to configured channels with schedules, throttling and silencing.

## Data flows

### Deployment tracking

```mermaid
sequenceDiagram
    participant Agent as Discovery Agent
    participant API as Control Plane API
    participant DB as Data Store
    participant Front as Web App

    Agent->>API: Detect Deployment change
    API->>DB: Store revision and images
    API->>API: Link incidents and rollout context
    Front->>API: Fetch deployment data
    API->>Front: Return revisions and linked state
```

### Cluster inventory and CronJob flow

```mermaid
sequenceDiagram
    participant Agent as Discovery Agent
    participant API as Control Plane API
    participant DB as Data Store
    participant Front as Web App

    Agent->>API: Send cluster metadata heartbeat
    Agent->>API: Upsert node snapshots
    Agent->>API: Sync CronJobs and Job executions
    API->>DB: Persist inventory and execution history
    Front->>API: Query clusters, nodes and CronJobs
    API->>Front: Return filtered inventory
```

### Scaling execution and rollback

```mermaid
sequenceDiagram
    participant User as User / API
    participant Scaling as Scaling Rules Agent
    participant K8S as Kubernetes API
    participant API as Scaling Rules API

    User->>API: Create or disable scaling rule
    API->>Scaling: Reconcile active state
    Scaling->>K8S: Apply temporary HPA values
    Scaling->>API: Store rollback state
    API->>Scaling: Rule disabled or expired
    Scaling->>K8S: Restore previous HPA state
```

## Authentication model

- users authenticate via Google OAuth or email/password
- agents authenticate with a cluster-specific token
- the web applications proxy backend calls server-side
- the MCP server exposes read-only scoped access tokens

## Storage model

- metadata such as organizations, projects, clusters, revisions, node snapshots and CronJobs is stored in a relational database
- failed CronJob log excerpts are stored with the execution records
- aggregated metrics and summaries are stored for fast dashboard queries

## Security highlights

- all agent communication uses HTTPS
- cluster tokens use constant-time comparison
- browsers never receive internal API tokens
- sanitized manifests preserve resource identities such as Secret names while redacting sensitive values
