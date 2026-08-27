---
title: "Data Collection"
---

This page explains what the current Moonin agents read from the cluster, what they send to the platform and what execution state they keep only long enough to complete a reconcile cycle.

## Discovery Agent data

### Deployment and revision inventory

For each tracked Deployment, Moonin can collect:

- deployment name and namespace
- desired, current and available replicas
- rollout strategy
- labels and annotations
- container images and tags
- service relationships
- revision number and revision type
- timestamps associated with the detected change

When the workload is Helm-managed, the agent also derives:

- release name
- chart name and version when available
- Helm revision number
- sanitized manifest-derived context for revision review

### Pod lifecycle and workload error signals

The Discovery Agent watches pods to report signals that help Moonin build the Errors and Revision context, including:

- restart count changes
- `CrashLoopBackOff`
- `OOMKilled`
- container readiness failures
- pod phase transitions such as `Pending`, `Running`, `Succeeded` and `Failed`

### HPA snapshots

Moonin stores HPA context associated with Deployments, including:

- minimum replicas
- maximum replicas
- target metrics
- behavior
- captured status at the time of sync

### Namespaces, services and topology

The agent also discovers:

- namespace names, labels and annotations
- service names, selectors, types and ports
- ingress and network policy inventory
- selected RBAC object metadata for topology context

### CronJob definitions

For each tracked CronJob, the agent sends:

- CronJob name
- namespace
- raw cron expression
- timezone if present
- concurrency policy
- suspend flag
- last schedule time
- last successful time
- active job count

### CronJob execution history

For each Job owned by a tracked CronJob, Moonin can store:

- Job name and UID
- execution status
- start time
- completion time
- duration
- pod name related to the failure
- failure reason
- failure message
- exit code
- up to the last 200 log lines for failed executions

### Node and cluster metadata

Node snapshots periodically include:

- node name
- capacity and allocatable CPU, memory, storage and pods
- conditions such as `Ready`, `MemoryPressure` and `DiskPressure`
- runtime, OS image, architecture and instance type
- region and zone when derivable

Cluster metadata heartbeats can include:

- Kubernetes version
- cloud provider
- cluster name and identifier when derivable
- region and zone
- node count
- connectivity status

!!! note
    Node pages show inventory snapshots, not live resource usage like `kubectl top`.

## Scaling Rules Agent state and evidence

The Scaling Rules Agent is not an inventory collector, but it still derives and transmits execution state.

### Data it reads during apply

To apply an action, the agent reads:

- target Deployment name and namespace from the template action
- current Deployment replica count
- current HPA that targets that Deployment, if one exists
- active template window, timezone, duration and enablement state from Moonin

### Data it persists temporarily on managed HPAs

To make rollback deterministic, the agent stores management annotations on the HPA, including:

- template id and action id
- template name
- execution `run_until`
- `priority_up` and `priority_down`
- whether the HPA is provisional
- original HPA spec when the HPA existed before Moonin
- original Deployment replica count
- original min and max replicas when applicable

### Events it sends back to Moonin

After apply or revert, the agent posts execution evidence such as:

- action id
- deployment and namespace
- min and max values requested by the action
- effective `run_until`
- whether the HPA was provisional
- revert reason, such as `expired` or `disabled`

## Collection model

The bundle combines two patterns:

- informer-based near real-time collection for the Discovery Agent
- periodic polling and reconciliation for the Scaling Rules Agent

This is intentional. Discovery follows cluster events, while scaling follows template state owned by the control plane.

## Filters and scope reduction

The chart exposes configuration to reduce what Discovery collects:

| Option | Effect |
|---|---|
| `ignore_namespaces` | Exclude whole namespaces from discovery |
| `ignore_resources` | Exclude matching resource globs |
| `ignore_node_labels` | Prevent selected node labels from being sent |

```yaml
log_level: info
ignore_namespaces:
  - kube-system
ignore_resources:
  - job/*
ignore_node_labels:
  - beta.kubernetes.io/arch
```

## What is not stored locally

- The agents do not keep a durable local database.
- Discovery keeps in-memory controller state and continuously reconciles with the platform.
- Scaling rollback context is carried on managed HPA annotations, not in a separate local store.
