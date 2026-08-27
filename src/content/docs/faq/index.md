---
title: "FAQ"
---

## Does the chart install more than one agent?

Yes. The current `moonin-agent` chart bundles the Discovery Agent and the Scaling Rules Agent.

## Are node values the same as `kubectl top`?

No. The Nodes page shows inventory snapshots based on capacity and allocatable values, not live CPU or memory consumption.

## Can Moonin show CronJob failures?

Yes. Moonin tracks CronJobs, Job executions and stores up to the last 200 log lines for failed runs.

## What happens when a scaling rule is disabled?

The Scaling Rules Agent should revert the HPA state to the previous baseline, just like it does when a rule reaches its scheduled end.

## Where do I create notification channels?

In the Admin Console, under the organization notification channels area. Policies in the main app only select existing channels.

## Does Moonin preserve Secret names in sanitized manifests?

Yes. Sensitive values are redacted, but resource identities such as Secret names are preserved for troubleshooting context.
