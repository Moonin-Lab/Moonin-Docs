# Quickstart

This quickstart assumes your cluster is already registered and the Helm chart is installed.

## 10-minute product tour

### 1. Confirm the cluster heartbeat

Open **Clusters** and verify:

- status is healthy
- provider metadata is populated
- namespaces and deployments are starting to appear

### 2. Open the overview dashboard

Use the **Overview** screen to validate:

- tracked clusters
- images found in the current scope
- CronJobs and recent executions
- active error and failure-rate signals

### 3. Inspect a node snapshot

Go to **Nodes** and verify the inventory:

- node readiness
- capacity vs allocatable CPU and memory
- instance type, zone and runtime
- captured timestamp

Node snapshots are inventory records, not live `kubectl top` usage.

### 4. Inspect revisions and images

From **Deployments**:

- open a service
- review its latest revision
- validate image names and tags
- inspect Helm metadata if the workload is Helm-managed

### 5. Validate CronJobs

Open **CronJobs** to see:

- raw cron expression
- readable schedule
- namespace and cluster scope
- recent executions
- failure logs when a Job run fails

### 6. Configure response policies

Create or update:

- **Alert Policies** for error signals
- **Event Notification Policies** for deployment or platform events

Notification channels are created in the **Admin Console** and then selected from the main app.
