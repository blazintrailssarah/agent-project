# ADR-002: LLM Provider Priority and Failover Behavior

| Field               | Value                                |
| ------------------- | ------------------------------------ |
| **Status**          | Accepted                             |
| **Date**            | 2026-02-14                           |
| **Decision makers** | Repo maintainers                     |
| **Consulted**       | AI agents (CrewAI reliability work)  |
| **Informed**        | Contributors running local/CI review |

---

## 📋 Context

CrewAI review runs need predictable behavior when a provider times out or lacks credit. The subsystem currently includes explicit provider resolution and fallback behavior in both orchestration code and local runner scripts.

---

## 🎯 Decision

Use the following provider order for CrewAI review execution:

1. NVIDIA NIM (`NVIDIA_API_KEY` or `NVIDIA_NIM_API_KEY`)
2. OpenRouter (`OPENROUTER_API_KEY`) fallback

Operational rules:

- Apply a shorter timeout for NVIDIA primary attempt.
- On NVIDIA failure, run one fallback attempt using the next available provider.
- Surface primary-provider failure reason in local output before fallback result.

---

## ⚡ Consequences

### Positive

- Deterministic provider selection and easier support triage.
- Review runs remain available during provider-specific outages/credit limits.

### Negative

- Multi-provider behavior increases environment variable complexity.

---

## 📋 Evidence in code

- `scripts/ci-local.sh` (`resolve_review_provider`, review timeout and fallback logic)
- `.crewai/utils/model_config.py` (provider key resolution and LLM initialization order)

---

## 🔗 References

- [CrewAI model config](../utils/model_config.py)
- [Local CI review runner](../../scripts/ci-local.sh)

---

_Last updated: 2026-02-14_
