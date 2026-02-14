# CrewAI ADR Index

This directory contains subsystem-local architecture decisions for `.crewai/`.

Use this log for CrewAI implementation decisions that do not change monorepo-wide policy.

If a local decision affects other subsystems or repo governance, mirror it in `agentic/adr/`.

---

## ADRs

| ADR                                                    | Title                                                     | Status   |
| ------------------------------------------------------ | --------------------------------------------------------- | -------- |
| [ADR-001](./ADR-001-crewai-decision-log-scope.md)      | CrewAI local ADR log scope and ownership                  | Accepted |
| [ADR-002](./ADR-002-provider-priority-and-failover.md) | LLM provider priority and failover behavior               | Accepted |
| [ADR-003](./ADR-003-local-quick-review-multipass.md)   | Local quick-review multi-pass synthesis and output schema | Accepted |

---

## Related

- [Global ADR governance](../../agentic/adr/ADR-006-federated-adr-governance.md)
- [CrewAI subsystem guide](../README.md)
