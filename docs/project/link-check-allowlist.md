# Link Check Allowlist Audit

| Pattern                         | Type                 | Reason                                              | Manual verification                                                     | Added                                                             | Review by  | Status     |
| ------------------------------- | -------------------- | --------------------------------------------------- | ----------------------------------------------------------------------- | ----------------------------------------------------------------- | ---------- | ---------- | ------ |
| `^https://github.com/org/repo($ | /)`                  | Placeholder external                                | Template placeholder URL for docs/examples; not a real project endpoint | Confirmed placeholder-only usage in `agentic/markdown_templates/` | 2026-02-15 | 2026-05-15 | Active |
| `^https://full-url/?$`          | Placeholder external | Citation placeholder used in template guidance text | Confirmed placeholder-only usage in template/style-guide examples       | 2026-02-15                                                        | 2026-05-15 | Active     |

Use this file as the required audit log for exclusions in `.lychee.toml`.
