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
- Final summary fallback formatting now prioritizes decision speed: executive summary + priority action list + specialist severity rollup + workflow guide + traceability, with a rebuilt end-of-report cost section that surfaces crew totals first and leaves per-call rows collapsed.
- Quick-review normalization now suppresses low-signal parser artifacts: non-JSON reviewer fallback summaries do not create synthetic findings, duplicate recommendation/fix payloads are deduplicated, and priority action extraction only promotes high-severity items.
- Specialist sanitization now enforces changed-file scope for file-linked findings, preventing parsed-result recovery artifacts from surfacing unrelated criticals in final summaries.
- Local/non-PR runs now skip persistent review-history updates, so `memory.json` no longer accumulates noisy local trend data; memory baseline was reset.
- Repository licensing/attribution policy clarified in source-of-truth docs: Apache-2.0 + top-level `NOTICE` preserved in redistributions with attribution to Superior Byte Works, LLC / Clayton Young (Boreal Bytes).
- Executive summary now prioritizes actionability over workflow narration (high-priority count, top risk, and immediate action window), and quick-review breakdowns prune repeated low-signal placeholder findings.
- Local full-review execution now runs an explicit four-stage multipass path (quality, architecture, security, synthesis) so call accounting and review coverage align with full-review expectations in local CI.
- Final summary formatting no longer forces horizontal-rule separators after every `</details>` block.
- Removed duplicate specialist status rows from the top workflow guide; specialist review status now appears only once in each specialist section.
- `scripts/ci-local.sh` now enforces single-run locking via `.ci-local.lock` and clears `.crewai/workspace` at startup to prevent stale artifact bleed-through between local runs.
- Specialist local execution now consistently uses structured domain-focused prompts per crew in full-review mode, reducing generic cross-domain findings and improving specialty signal quality.
- Cost reporting now includes agent-level attribution in addition to crew-level totals.
- Introduced complete-repo review mode: `--complete-full-review` in local CI sets `crewai:complete-full-review` and runs full review plus all specialists under complete-repository scope semantics.
- Router contract updated so GitHub PR labels containing `crewai:complete-full-review` trigger the same full+all-specialist expansion path as `crewai:full-review`.
- Fixed reusable review workflow context-pack parsing to support list-shaped `commits.json` output, eliminating GitHub Actions failure `AttributeError: 'list' object has no attribute 'get'` in PR data preparation.

---

## 🔗 References

- [PR-#1](../pr/pr-00000001-agentic-docs-and-monorepo-modernization.md)
- [Issue-#2](issue-00000002-provider-priority-fail-fast-review-cost-visibility.md)
- [Sprint board](../kanban/sprint-2026-w07-agentic-template-modernization.md)

---

_Last updated: 2026-02-14 19:16 EST_
