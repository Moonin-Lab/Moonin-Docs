---
title: "Security Model"
---

Moonin is designed so the cluster-side bundle stays narrow, auditable and separated from user-facing application credentials.

## Cluster credentials

- The chart stores `PROJECT_ID`, `CLUSTER_ID` and `CLUSTER_TOKEN` in a shared Kubernetes Secret.
- All bundled agents reuse that secret.
- Cluster credentials authenticate the cluster to Moonin. They are not browser session credentials.
- Cluster tokens can be rotated without re-registering the cluster object.

## Transport and trust boundary

- Agent communication with the platform uses HTTPS.
- User-facing applications proxy their own server-side requests and do not expose internal cluster credentials to browsers.
- The cluster authenticates as a cluster. Users authenticate separately through the Moonin applications.

## Discovery data sanitization

When the Discovery Agent derives revision context from Helm releases or manifests:

- sensitive values are redacted before storage
- resource identities remain visible
- troubleshooting context is preserved without storing secret payloads

That means Moonin can still show names such as Secrets, ConfigMaps, workloads and namespaces while keeping sensitive content out of the stored payload.

## Scaling ownership and rollback safety

The Scaling Rules Agent protects HPA ownership in several ways:

- it annotates managed HPAs with template and action ownership
- it stores the original HPA spec before overwriting an existing HPA
- it stores the original Deployment replica count before changing the execution baseline
- it refuses to take over an HPA already managed by a different active template or action

These controls are what make scheduled scaling reversible instead of merely imperative.

## Mutation boundaries

- The Discovery Agent does not mutate workloads.
- The Scaling Rules Agent only mutates Deployments and HPAs involved in an active scaling template.
- If the Scaling Rules Agent creates an HPA only for the execution window, that HPA is deleted during revert after the original Deployment baseline is restored.

## What the bundle does not do

- It does not expose cluster credentials to end users.
- It does not store full secret values in the platform.
- It does not act as a generic traffic proxy or privileged cluster shell.
