# agent-project: AGENTS.md-First Agentic Coding Template

`agent-project` is a practical starter template for teams shipping with coding agents.

It is built around an `AGENTS.md` entrypoint and an "everything as code" workflow where standards, plans, PR records, issues, boards, and review policies live in the repository as versioned markdown files.

If you want one repository where humans and agents read the same rules, run the same checks, and leave the same audit trail, this template is designed for that.

---

## What this template gives you

- A production-ready `AGENTS.md` entrypoint and agent operating framework in `agentic/`
- Local CI orchestration via `./scripts/ci-local.sh` plus matching GitHub Actions workflows
- Optional multi-agent CrewAI review pipeline with quick, full, and complete-full review modes
- Versioned docs/templates for PRs, issues, kanban, ADRs, markdown style, and Mermaid diagrams
- Local-first review memory and suppression tooling (`scripts/memory.sh`) for repeatable signal quality

---

## Quickstart

```bash
git clone https://github.com/borealBytes/agent-project.git
cd agent-project
pnpm install
./scripts/ci-local.sh
```

Agent review modes:

```bash
./scripts/ci-local.sh --review
./scripts/ci-local.sh --full-review --step review
./scripts/ci-local.sh --complete-full-review --step review
```

---

## Who this is for

- Teams using agentic coding tools that natively read `AGENTS.md`
- Teams using web-based agents that can ingest repo instructions and apply git diffs
- Teams using IDE/CLI agents (for example: OpenCode, RooCode, Claude Code, GitHub Copilot in VS Code)
- Teams that want auditable, repo-native process standards instead of UI-only project metadata

---

## Usage modes

### 1) Web-based or hosted agent workflow

Use this repo as a remote source of truth:

- Point the agent to `AGENTS.md` as the entrypoint
- Connect the repository (or provide a diff-based workflow)
- Keep all standards and tracking records in-repo so both humans and agents read the same source

### 2) Local checkout workflow

Run from your local clone for day-to-day development, validation, and review orchestration.

---

## Review modes

| Mode          | Command                                                      | What it does                                            | When to use                                     |
| ------------- | ------------------------------------------------------------ | ------------------------------------------------------- | ----------------------------------------------- |
| Quick         | `./scripts/ci-local.sh --review`                             | Fast triage-oriented review path                        | Day-to-day iteration                            |
| Full          | `./scripts/ci-local.sh --full-review --step review`          | Deeper synthesis plus broader specialist selection      | Risky or broad code changes                     |
| Complete Full | `./scripts/ci-local.sh --complete-full-review --step review` | Full review plus all specialists in complete-repo scope | Pre-merge hardening or policy-sensitive changes |

The value is layered assurance: speed when you need flow, depth when you need confidence, and complete specialist coverage when the change touches multiple risk domains.

---

## Specialist reviews and customization

Specialists are configured in `.crewai/` and can be adapted to your domain:

- Agent definitions: `.crewai/config/agents.yaml`
- Task contracts: `.crewai/config/tasks/*.yaml`
- Crew wiring: `.crewai/crews/*`
- Domain decisions and policy rationale: `.crewai/adr/`

You can add organization-specific legal/compliance/security context as markdown in-repo and route specialist prompts to those files so reviews are grounded in your actual jurisdiction and standards every run.

---

## Everything as code

This template treats process records as first-class code artifacts:

- PR records: `docs/project/pr/`
- Issue records: `docs/project/issues/`
- Kanban boards: `docs/project/kanban/`
- Repo-wide decisions: `agentic/adr/`
- Subsystem decisions: local `adr/` directories (for example `.crewai/adr/`)

This keeps your delivery history portable, reviewable in git, and readable by both humans and agents without extra platform APIs.

---

## Recommended local editor setup

For local docs review and diagram rendering in VS Code:

- Use built-in Markdown preview for `.md` files
- Install a Mermaid-capable markdown preview extension
- Validate locally with `./scripts/ci-local.sh --step link-check`

---

## Start here

- Agent entrypoint: `AGENTS.md`
- Agent framework guide: `agentic/README.md`
- CI workflow architecture: `.github/workflows/README.md`
- Scripts guide: `scripts/README.md`
