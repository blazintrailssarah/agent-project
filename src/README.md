# Source Code

> Production Python applications, libraries, and utilities.

---

## 📋 Purpose

This directory holds production-grade Python code:

- **Applications** — standalone tools, CLI utilities, web services
- **Libraries** — shared modules used across the project
- **Integrations** — connectors to external APIs and services
- **Utilities** — helper scripts that have graduated from `notebooks/`

---

## 📂 Organization

```text
src/
├── README.md              # This file
├── apps/                  # Standalone applications
│   └── {app-name}/        # Each app gets its own directory
│       ├── __init__.py
│       ├── main.py
│       └── ...
├── libs/                  # Shared libraries
│   └── {lib-name}/
│       ├── __init__.py
│       └── ...
└── utils/                 # Small utilities and helpers
    └── ...
```

Create subdirectories as needed. Each application or library should be self-contained with its own `__init__.py`.

---

## 🔧 Setup

### Virtual environment

```bash
# Create (if not already created)
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
# .venv\Scripts\activate    # Windows

# Install project dependencies
pip install -r requirements.txt   # if present
```

### Adding a new application

```bash
mkdir -p src/apps/my-app
touch src/apps/my-app/__init__.py
touch src/apps/my-app/main.py
```

Every application should include:

- `__init__.py` — package marker
- `main.py` — entry point
- `README.md` — what the app does and how to run it

---

## 🚨 Rules

1. **Never commit secrets** — use `.env` files and environment variables
2. **Type hints required** — all functions must have type annotations
3. **Docstrings required** — all public functions and classes need docstrings
4. **Tests live in `tests/`** — mirror the `src/` structure in the test directory
5. **Idempotent scripts** — all scripts must be safe to run multiple times (see [idempotent design patterns](../agentic/idempotent_design_patterns.md))
6. **`__pycache__/` is gitignored** — Python bytecache is excluded automatically

---

## 🔗 References

- [notebooks/](../notebooks/) — Prototyping and exploration (code graduates here)
- [.crewai/](../.crewai/) — CrewAI review system
- [agentic/](../agentic/) — Agent instructions and standards
- [agentic/idempotent_design_patterns.md](../agentic/idempotent_design_patterns.md) — Script design standards

---

_Part of the [opencode](https://github.com/borealBytes/agent-project) template project._
