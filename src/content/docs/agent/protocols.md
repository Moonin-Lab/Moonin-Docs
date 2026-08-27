---
title: "Communication Protocols"
---

The current Moonin agents communicate with the control plane over HTTPS using cluster-scoped credentials.

## Credentials and headers

Both agents receive these values from the shared Kubernetes Secret created by the chart:

- `PROJECT_ID`
- `CLUSTER_ID`
- `CLUSTER_TOKEN`

The cluster token is sent on agent-to-platform requests through the `X-Cluster-Token` header. Some internal Discovery Agent calls also include a bearer header for compatibility, but the trust model is still cluster-scoped, not user-scoped.

## Main destinations

| Flow | Destination | Used by | Purpose |
|---|---|---|---|
| Inventory sync | `api-discover.moonin.app` | Discovery Agent | namespaces, Deployments, revisions, errors, images, HPAs, CronJobs and nodes |
| Cluster heartbeat | `api-discover.moonin.app` | Discovery Agent | cluster availability and cloud metadata |
| Template polling | `api-scaling-rules.moonin.app` | Scaling Rules Agent | list templates for the cluster |
| Action polling | `api-scaling-rules.moonin.app` | Scaling Rules Agent | load the actions for an active template |
| Execution events | `api-scaling-rules.moonin.app` | Scaling Rules Agent | notify apply and revert results |

## Discovery Agent request model

The Discovery Agent uses two communication patterns:

- **Warm-up synchronization** for namespaces, Deployments and CronJobs when the leader starts.
- **Steady-state submissions** triggered by informers and periodic loops.

High-level flow:

1. Read resources from the Kubernetes API.
2. Normalize and sanitize the payload when needed.
3. Batch submissions where appropriate.
4. Send the result to the Discovery API using cluster-scoped authentication.

## Scaling Rules Agent request model

The Scaling Rules Agent runs a fixed reconcile loop every 30 seconds:

1. `GET` the templates available for the cluster.
2. Evaluate which ones should run now.
3. `GET` the actions for each active template.
4. Apply cluster-side HPA changes.
5. `POST` execution or revert events back to the Scaling Rules API.

## Template evaluation protocol

The platform returns the template metadata and the agent evaluates:

- whether the template is enabled
- whether the current time is still before `valid_until`
- whether a manual execution is currently marked as `running`
- whether the current time falls inside the scheduled execution window in the configured timezone

That means the control plane owns the template definition, while the cluster-side agent owns the final "run now or not" decision for that cluster and that moment in time.

## Cloud metadata lookups

Before sending cluster metadata, the Discovery Agent may query cloud metadata endpoints or derive provider context from node labels. This helps Moonin classify the cluster as GKE, EKS, AKS or an unknown or on-prem environment.

## Browser and API boundary

Users do not call the cluster-facing APIs directly from the browser. `app.moonin.app` and `app-admin.moonin.app` sit behind server-side application boundaries and enforce user scope there, while the agents authenticate as clusters.
