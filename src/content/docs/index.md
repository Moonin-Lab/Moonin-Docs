---
title: "Moonin Documentation"
---

<section class="moonin-docs-hero">
  <div class="moonin-eyebrow">Moonin Documentation</div>
  <h1>Operate Kubernetes with context, not guesswork.</h1>
  <p>Learn how Moonin connects cluster inventory, deployments, revisions, incidents and notifications into one operational workspace.</p>
  <div class="moonin-hero-actions">
    <a href="getting-started/">Get started</a>
    <a href="es/">Ver documentación en español</a>
  </div>
</section>

## What Moonin connects

Moonin is a Kubernetes operations platform centered on five connected jobs:

- model the runtime hierarchy of your estate
- track every rollout as a revision
- capture runtime failures with rollout context
- route notifications through reusable policies
- keep organizational access, clusters and channels governed from one place

This documentation is written so an operator can move from onboarding to day-2 operations without depending on hidden product knowledge.

## Language entry points

| Language | Start here |
|---|---|
| English | [Getting Started](getting-started/) |
| Español | [Documentacion en espanol](es/) |

## Resource hierarchy

The main mental model in Moonin is hierarchical. Most screens, filters and permissions follow this chain:

```mermaid
flowchart TD
    O[Organization]
    P[Project]
    C[Cluster]
    N[Namespace]
    D[Deployment or Service]
    R[Revision]
    E[Error]
    CJ[CronJob]

    O --> P
    P --> C
    C --> N
    N --> D
    D --> R
    R --> E
    N --> CJ
```

## What each level means

- `Organization` is the tenant boundary for users, groups, billing, notification channels, policies and SSO settings.
- `Project` groups clusters that belong to the same business domain, team or environment.
- `Cluster` is the registered Kubernetes target connected through the Moonin agent.
- `Namespace` scopes workloads inside a cluster.
- `Deployment` is the rollout unit tracked by Moonin for revision and incident correlation.
- `Service` is the traffic-facing view of a workload and is used to explore logs, events, metrics and dependencies.
- `Revision` is the immutable snapshot created for a rollout.
- `CronJob` is the scheduled execution unit tracked separately from deployment revisions.

## Core product flows

### 1. Onboard and discover

```mermaid
flowchart LR
    A[Admin Console]
    B[Create organization]
    C[Create project]
    D[Register cluster]
    E[Install Moonin agent]
    F[Sync inventory]

    A --> B --> C --> D --> E --> F
```

### 2. Follow a rollout

```mermaid
flowchart LR
    A[Deployment changes]
    B[Revision created]
    C[Images and services attached]
    D[Cloud and HPA context attached]
    E[Release visible in Releases and Deployments]

    A --> B --> C --> D --> E
```

### 3. Investigate an incident

```mermaid
flowchart LR
    A[Pod or job failure]
    B[Moonin records error]
    C[Error linked to revision and workload]
    D[Policies evaluated]
    E[Operator opens Errors or History]
    F[Mitigate or acknowledge]

    A --> B --> C --> D --> E --> F
```

### 4. Notify the right channel

```mermaid
flowchart LR
    A[Organization notification channels]
    B[Alert or event policy]
    C[Scope and timing match]
    D[Window and enabled checks]
    E[Slack, Teams or VictorOps delivery]

    A --> B --> C --> D --> E
```

## Access model at a glance

Moonin combines baseline membership with fine-grained roles:

- `organization.owner` has full control of the organization.
- Membership roles are `viewer`, `editor` and `admin`.
- `viewer` is the minimum role and follows least-privilege by default.
- By default, `viewer` can list organizations and depends on administrator-granted permissions for additional access.
- Direct user roles can grant feature-specific permissions.
- Group roles let teams inherit the same permissions without editing users one by one.
- Some screens also enforce feature permissions such as revision viewing, error RCA, policy editing or cluster administration.

The full operating model is described in [Administration](administration/index.md) and [Azure AD](integrations/azure-ad.md).

## Documentation map

| Need | Page |
|---|---|
| Understand releases, revisions and rollout context | [Revision History](revisions/index.md) |
| Work with deployments and image inventory | [Deployments & Images](deployments/index.md) |
| Operate clusters and inspect node inventory | [Clusters & Nodes](clusters/index.md) |
| Understand services, CronJobs and execution history | [Workloads, Services & CronJobs](workloads/index.md) |
| Investigate active and historical failures | [Incidents & Errors](incidents/index.md) |
| Configure channels and understand delivery logic | [Notifications](notifications/index.md) |
| Configure alerting, event routing and scaling automation | [Policies & Governance](policies/index.md) |
| Manage organizations, projects, users, groups and clusters | [Administration](administration/index.md) |
| Set up Microsoft Entra ID per organization | [Azure AD](integrations/azure-ad.md) |
