# Limitations & Scope

This page documents the intentional boundaries of the current public agent bundle.

## Discovery Agent limits

- Node pages show capacity and allocatable snapshots, not live usage sampling.
- Provider detection is best effort and depends on cloud metadata access or useful node labels.
- CronJob execution history depends on child Jobs remaining visible and not being excluded by filters.
- Failed execution logs are stored only as a tail of up to 200 lines, not as full pod log archives.
- Namespaces and resources excluded through ignore rules are completely omitted from discovery and related history.
- Discovery helps explain runtime state in Moonin, but it is not a full observability pipeline or a replacement for dedicated metrics, traces or long-term log retention tools.

## Scaling Rules Agent limits

- The current implementation targets Deployments through HPAs.
- Scaling windows are driven by template state from Moonin plus the agent's local time-based evaluation at reconcile time.
- Reverts happen on the next reconcile cycle, so disablement or expiration is not instant to the millisecond.
- If a target Deployment has no HPA, the agent may create a provisional managed HPA for the execution window.
- Rollback quality depends on the original baseline captured before Moonin took control of the HPA.
- External HPA or replica changes performed after that baseline is captured can affect the eventual rollback target.
- Only one managed template ownership context can control a given HPA at a time.

## Bundle boundaries

- The bundle does not proxy end-user requests into the cluster.
- The bundle does not create a durable local data store.
- The public documentation explains supported behavior, not internal commercial heuristics of the wider Moonin platform.
