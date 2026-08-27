---
title: "Root Cause Analysis"
---

Moonin Root Cause Analysis combines deployment history, runtime context and policy signals to shorten the path from symptom to likely cause.

## Inputs used by RCA

- revisions and image changes
- cluster and namespace scope
- recent incidents
- node and workload context
- CronJob execution history when automation jobs are involved

## Useful operator questions

- did the issue start after a rollout?
- is a failed scheduled job contributing to the incident?
- is the problem limited to one cluster or broader?
- did a temporary scaling rule change capacity shortly before the incident?

## Recommended workflow

1. start from the active error or workload
2. inspect the latest revision and recent CronJob activity
3. review cluster and node context
4. confirm whether a policy, silence or scaling action changed the response path
