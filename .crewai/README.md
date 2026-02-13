# CrewAI Code Review System

> Multi-agent AI code review for GitHub pull requests. 27 specialized agents across 14 crews covering security, legal, finance, documentation, marketing, science, government compliance, and business strategy.

---

## 📋 Overview

This directory contains a CrewAI-powered code review system that runs automatically on pull requests via GitHub Actions or locally via `./scripts/ci-local.sh --review`.

**System at a glance:**

| Metric                    | Value                                                                                                 |
| ------------------------- | ----------------------------------------------------------------------------------------------------- |
| **Agents**                | 27 specialized agents                                                                                 |
| **Crews**                 | 14 review crews                                                                                       |
| **Tasks**                 | 29 sequential tasks                                                                                   |
| **Specialist domains**    | 9 (security, legal, finance, docs, agentic, marketing, science, government, strategy)                 |
| **Multi-agent pipelines** | Legal (4 agents), Marketing (3), Strategy (3), Full Review (3), Quick Review (3), CI Log Analysis (3) |
| **Output**                | Structured JSON per crew + markdown summary                                                           |

---

## 🏗️ Architecture

### Crew pipeline

```
Router → CI Log Analysis → Quick Review → [Full Review] → [Specialist Crews] → Final Summary
                                              ↑                    ↑
                                        (if label:               (if labels or
                                         full-review)             autodetect)
```

**Always-run crews:** Router, CI Log Analysis, Quick Review, Final Summary

**Label-triggered crews:** Full Review, and any of the 9 specialist crews

**`crewai:full-review` label:** Runs ALL specialist crews

### Specialist crews

| Crew          | Agents                                             | Label               | Domain                                                                                        |
| ------------- | -------------------------------------------------- | ------------------- | --------------------------------------------------------------------------------------------- |
| Security      | 1 (owasp_sentinel)                                 | `crewai:security`   | OWASP-grade vulnerability analysis                                                            |
| Legal         | 4 (license → US regulatory → intl trade → privacy) | `crewai:legal`      | OSS licenses, 50-state US law, export controls, global privacy (GDPR, CCPA, LGPD, PIPL, etc.) |
| Finance       | 1 (revenue_auditor)                                | `crewai:finance`    | Billing logic, payment flows, SOX, PCI-DSS                                                    |
| Documentation | 1 (docs_curator)                                   | `crewai:docs`       | README accuracy, API docs, code examples                                                      |
| Agentic       | 1 (agentic_steward)                                | `crewai:agentic`    | AGENTS.md compliance, convention enforcement                                                  |
| Marketing     | 3 (brand → global GTM → compliance)                | `crewai:marketing`  | Copy quality, i18n, regional advertising law, dark patterns                                   |
| Science       | 1 (repro_scientist)                                | `crewai:science`    | Reproducibility, statistical rigor, data leakage                                              |
| Government    | 1 (public_sector_compliance)                       | `crewai:government` | WCAG 2.1 AA, Section 508, audit trails                                                        |
| Strategy      | 3 (impact → expansion → competitive)               | `crewai:strategy`   | Business impact, global expansion readiness, competitive positioning                          |

---

## 📁 Directory structure

```
.crewai/
├── main.py                          # Entry point and orchestration
├── pyproject.toml                   # Python dependencies
├── .env.example                     # Environment variable template
├── config/
│   ├── agents.yaml                  # 27 agent definitions
│   └── tasks/
│       ├── router_tasks.yaml        # 1 task
│       ├── ci_log_analysis_tasks.yaml  # 4 tasks (3 agents)
│       ├── quick_review_tasks.yaml  # 3 tasks (3 agents)
│       ├── full_review_tasks.yaml   # 4 tasks (3 agents)
│       ├── security_review_tasks.yaml
│       ├── legal_review_tasks.yaml  # 4 tasks (4 agents)
│       ├── finance_review_tasks.yaml
│       ├── documentation_review_tasks.yaml
│       ├── agentic_review_tasks.yaml
│       ├── marketing_review_tasks.yaml  # 3 tasks (3 agents)
│       ├── science_review_tasks.yaml
│       ├── government_review_tasks.yaml
│       ├── strategy_review_tasks.yaml   # 3 tasks (3 agents)
│       └── final_summary_tasks.yaml
├── crews/
│   ├── __init__.py
│   ├── router_crew.py
│   ├── ci_log_analysis_crew.py
│   ├── quick_review_crew.py
│   ├── full_review_crew.py
│   ├── security_review_crew.py
│   ├── legal_review_crew.py
│   ├── finance_review_crew.py
│   ├── documentation_review_crew.py
│   ├── agentic_review_crew.py
│   ├── marketing_review_crew.py
│   ├── science_review_crew.py
│   ├── government_review_crew.py
│   ├── strategy_review_crew.py
│   └── final_summary_crew.py
├── tools/
│   ├── workspace_tool.py            # File I/O for crew workspace
│   ├── cost_tracker.py              # API call cost tracking
│   ├── memory_manager.py            # Persistent review memory (JSON default, mem0 optional)
│   ├── github_tools.py              # Git diff and commit tools
│   ├── pr_metadata_tool.py          # PR metadata extraction
│   ├── ci_tools.py                  # CI log analysis tools
│   └── diff_parser.py               # Diff parsing utilities
├── utils/
│   ├── model_config.py              # LLM configuration and rate limiting
│   └── specialist_output.py         # Crew registry, output schema validation, autodetect
├── memory/
│   ├── memory.json                  # Persistent review memory (local)
│   └── suppressions.json            # Finding suppression rules
├── workspace/                       # Runtime workspace (created per run, gitignored)
└── tests/
    ├── conftest.py
    ├── test_workspace_tool.py
    ├── test_cost_tracker.py
    ├── test_github_tools.py
    ├── test_pr_metadata_tool.py
    ├── test_ci_output_parser_tool.py
    ├── test_specialist_output.py    # Registry, validation, autodetect tests
    └── test_crew_integrity.py       # Cross-reference and structure tests
```

---

## ⚡ Quick start

### Local review

```bash
# From repo root
./scripts/ci-local.sh --review
```

The script will prompt for `OPENROUTER_API_KEY` if not set. It cleans the workspace, generates a diff, and runs the full crew pipeline.

### GitHub Actions

1. Add `OPENROUTER_API_KEY` to repository secrets (Settings → Secrets → Actions)
2. Push a PR — the review runs automatically
3. Add labels to trigger specialist crews (e.g., `crewai:security`, `crewai:legal`)
4. Add `crewai:full-review` to run ALL specialist crews

---

## ⚙️ Configuration

### Environment variables

Copy `.env.example` to `.env` and set:

| Variable             | Required | Description                                                               |
| -------------------- | -------- | ------------------------------------------------------------------------- |
| `OPENROUTER_API_KEY` | Yes      | API key from [openrouter.ai/keys](https://openrouter.ai/keys)             |
| `CREWAI_MODEL`       | No       | Override default model (default: configured in `model_config.py`)         |
| `USE_MEM0_CLOUD`     | No       | Set to `true` to enable mem0 cloud memory (default: off, uses local JSON) |
| `MEM0_API_KEY`       | No       | Only needed if `USE_MEM0_CLOUD=true`                                      |

### Model selection

Edit `utils/model_config.py` to change the default model. The system uses OpenRouter for model access. Any OpenRouter-compatible model works.

### Customizing agents

Edit `config/agents.yaml` — each agent has `role`, `goal`, and `backstory` fields that control its behavior.

### Customizing tasks

Edit the relevant YAML in `config/tasks/` — each task has `description` (the agent's instructions) and `expected_output`.

---

## 🔬 Testing

```bash
cd .crewai
python3 -m pytest tests/ -v
```

97 tests covering:

- Workspace tool operations
- Cost tracker functionality
- GitHub tools and PR metadata
- CI output parsing
- Specialist crew registry (9 crews, labels, prefixes, output files)
- Output schema validation (severity counts, findings format, ID prefixes)
- Autodetect heuristics (file pattern matching for crew suggestions)
- Crew integrity (all 14 crew files compile, reference valid agents and tasks)
- Cross-reference validation (27 agents ↔ 29 tasks ↔ 14 YAML files)

---

## 📊 Output files

Each crew writes structured JSON to the workspace directory. The final summary crew reads all outputs and produces `final_summary.md`.

| File                                | Written by      | Schema                                                |
| ----------------------------------- | --------------- | ----------------------------------------------------- |
| `router_decision.json`              | Router          | Workflows, specialist crews, autodetect suggestions   |
| `ci_summary.json`                   | CI Log Analysis | Failed jobs, error evidence, fix recommendations      |
| `quick_review.json`                 | Quick Review    | Critical issues, warnings, suggestions                |
| `full_review.json`                  | Full Review     | Architecture, security, performance, testing findings |
| `security_review.json`              | Security        | OWASP findings with SEC- prefixed IDs                 |
| `legal_review.json`                 | Legal           | Multi-jurisdiction findings with LEGAL- prefixed IDs  |
| `finance_review.json`               | Finance         | Financial control findings with FIN- prefixed IDs     |
| `documentation_review.json`         | Documentation   | Doc quality findings with DOC- prefixed IDs           |
| `agentic_consistency_review.json`   | Agentic         | Convention findings with AGENT- prefixed IDs          |
| `marketing_review.json`             | Marketing       | Copy and GTM findings with MKT- prefixed IDs          |
| `science_review.json`               | Science         | Reproducibility findings with SCI- prefixed IDs       |
| `government_regulatory_review.json` | Government      | Accessibility findings with GOV- prefixed IDs         |
| `strategic_review.json`             | Strategy        | Business impact findings with STRAT- prefixed IDs     |
| `final_summary.md`                  | Final Summary   | Markdown rollup of all crew outputs                   |

### Standardized specialist output schema

All 9 specialist crews write the same JSON schema:

```json
{
  "summary": "1-3 sentences: what matters most and why.",
  "severity_counts": { "critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0 },
  "findings": [
    {
      "id": "PREFIX-001",
      "title": "Short title",
      "severity": "critical|high|medium|low|info",
      "file": "path/to/file",
      "description": "What changed and why it matters",
      "recommendation": "Concrete fix or next step",
      "verification": "How to prove the fix works"
    }
  ]
}
```

---

## 🔒 Security

- `OPENROUTER_API_KEY` stored in GitHub Secrets (encrypted at rest)
- `GITHUB_TOKEN` automatically provided by GitHub Actions with minimal permissions
- No secrets logged or exposed in output
- Local memory (`memory.json`) stays in repo, gitignored from workspace artifacts
- mem0 cloud integration is completely off by default
