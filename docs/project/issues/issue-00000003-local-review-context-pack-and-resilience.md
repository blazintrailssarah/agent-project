# Issue-00000003: Local Review Context Pack and Specialist Resilience

| Field              | Value                                                                               |
| ------------------ | ----------------------------------------------------------------------------------- |
| **Issue**          | [#3](https://github.com/borealBytes/opencode/issues/3)                              |
| **Type**           | ✨ Feature request                                                                  |
| **Priority**       | P1                                                                                  |
| **Requester**      | Human                                                                               |
| **Assignee**       | Human + AI agents                                                                   |
| **Date requested** | 2026-02-14                                                                          |
| **Status**         | In progress                                                                         |
| **Target release** | Sprint W07                                                                          |
| **Shipped in**     | [PR-#1](../pr/pr-00000001-agentic-docs-and-monorepo-modernization.md) (in progress) |

---

## 📋 Summary

### Problem statement

Local `--review` and `--full-review` needed a more resilient analysis path when tool-write persistence or provider behavior degraded. Quality also dropped on oversized diffs because specialists consumed raw context inconsistently.

### Proposed solution

Add a context-pack contract and resilient local structured-review path with non-blind retry and schema validation, so quick/full/specialist outputs stay actionable and comprehensive.

---

## 🎯 Success criteria

- [x] Local run generates compact `context_pack.json` and `context_pack.md`
- [x] Local full review can complete through structured synthesis without CrewAI tool-write dependency
- [x] Local specialist reviews use targeted retry with validation-based repair (not blind retry loops)
- [x] `validation_report.json` captures artifact validity and provenance
- [x] `--step review` passes for quick and full-review paths with specialist output files present
- [x] Specialist crews can selectively inspect repo context via tools (`FileContentTool`, `RelatedFilesTool`, `CommitInfoTool`, `CommitDiffTool`) while staying diff-first
- [x] Specialist outputs are non-simulated by policy; no-relevant domains emit explicit not-applicable zero-finding results

---

## 🔍 Scope flow

```mermaid
flowchart LR
    accTitle: Local Review Resilience Flow
    accDescr: Local review now builds a context pack, runs quick and full synthesis, validates specialist outputs, and records validation provenance before final summary assembly.

    prep[📥 Build context pack] --> quick[⚡ Quick review]
    quick --> full[🔍 Full review synthesis]
    full --> specialists[🧠 Specialist reviews]
    specialists --> validate[✅ Validate outputs]
    validate --> ledger[📝 validation_report.json]
    ledger --> summary[📋 Final summary]

    classDef primary fill:#dbeafe,stroke:#2563eb,stroke-width:2px,color:#1e3a5f
    classDef success fill:#dcfce7,stroke:#16a34a,stroke-width:2px,color:#14532d

    class prep,quick,full,specialists primary
    class validate,ledger,summary success
```

---

## ✅ Implementation notes

- `scripts/ci-local.sh` now writes `scope.json`, `context_pack.json`, and `context_pack.md` for local review context discipline.
- `.github/workflows/crewai-review-reusable.yml` now writes the same context artifacts (`scope.json`, `context_pack.json`, `context_pack.md`, `commit_messages.txt`) for GitHub Actions parity.
- `.crewai/main.py` now includes local structured full/specialist review paths with schema-key checks and targeted retry.
- Specialist output normalization now repairs IDs/severity/required fields before validation.
- All specialist crews now include selective-retrieval tools in addition to `WorkspaceTool`, enabling targeted repo exploration without loading the entire repo context.
- Local specialist orchestration now executes the actual specialist crews first and persists parsed-result recovery when tool-side file writes are missing, preserving multi-turn/tool-driven analysis before structured fallback.
- Specialist preflight relevance checks now prevent simulated domain output: if no domain-relevant changed files are detected, the specialist writes a deterministic not-applicable output with zero findings.
- Latest verification rerun confirms this behavior in full local review: finance and data engineering both emitted `no-relevant-changes` artifacts in `validation_report.json` with zero findings, while all 13 review workflows completed successfully.

---

## 🔗 References

- [PR-#1](../pr/pr-00000001-agentic-docs-and-monorepo-modernization.md)
- [Issue-#2](issue-00000002-provider-priority-fail-fast-review-cost-visibility.md)
- [Sprint board](../kanban/sprint-2026-w07-agentic-template-modernization.md)

---

_Last updated: 2026-02-14 17:27 EST_
