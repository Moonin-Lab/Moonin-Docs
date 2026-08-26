# Glossary

**Organization**
: Top-level Moonin account containing users, projects, clusters and notification channels.

**Project**
: Logical grouping used to organize clusters and workloads.

**Cluster**
: A Kubernetes cluster registered in Moonin and authenticated with a cluster token.

**Discovery Agent**
: In-cluster component that discovers resources, sends revisions, node snapshots, cluster metadata and CronJob execution history.

**Scaling Rules Agent**
: In-cluster component that applies temporary HPA changes and restores the previous state when rules expire or are disabled.

**Revision**
: Immutable rollout checkpoint for a deployment.

**CronJob execution**
: A Job run created by a CronJob, captured by Moonin with status, timing and optional failure logs.

**Notification channel**
: Organization-managed delivery target such as Slack, Teams or another supported connector.

**Alert policy**
: Rule that evaluates operational failures and routes them to channels.

**Event notification policy**
: Rule that routes platform or deployment events to channels.

**Rollback state**
: Stored HPA baseline used by the Scaling Rules Agent to revert temporary scaling changes.
