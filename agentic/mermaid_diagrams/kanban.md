# Kanban Board

> **Back to [Style Guide](../mermaid_style_guide.md)** — Read the style guide first for emoji, color, and accessibility rules.

**Syntax keyword:** `kanban`
**Best for:** Task status boards, workflow columns, work-in-progress visualization, sprint status
**When NOT to use:** Task timelines/dependencies (use [Gantt](gantt.md)), process logic (use [Flowchart](flowchart.md))

> ⚠️ **Accessibility:** Kanban boards do **not** support `accTitle`/`accDescr`. Always place a descriptive _italic_ Markdown paragraph directly above the code block.

---

## Exemplar Diagram

_Kanban board showing the current sprint's work items distributed across four workflow columns, with emoji indicating column status:_

```mermaid
kanban
    column1["📋 Backlog"]
        task1["🔐 Upgrade auth library"]
        task2["🛡️ Add rate limiting"]
        task3["📚 Write API docs"]

    column2["🔧 In Progress"]
        task4["📊 Build dashboard"]
        task5["🐛 Fix login bug"]

    column3["🔍 In Review"]
        task6["💰 Refactor payments"]

    column4["✅ Done"]
        task7["📊 Deploy monitoring"]
        task8["⚙️ Update CI pipeline"]
```

---

## Tips

- Name columns with **status emoji** for instant visual scanning
- Add **domain emoji** to tasks for quick categorization
- Keep to **3–5 columns**
- Limit to **3–4 items per column** (representative, not exhaustive)
- Items are simple text descriptions — keep concise
- Good for sprint snapshots in documentation
- **Always** pair with a Markdown text description above for screen readers

---

## Template

_Description of the workflow columns and what the board represents:_

```mermaid
kanban
    col1["📋 To Do"]
        item1["🔧 Task description"]
        item2["📝 Task description"]

    col2["🔧 In Progress"]
        item3["⚙️ Task description"]

    col3["✅ Done"]
        item4["🚀 Task description"]
```

---

## Complex Example

_Sprint W07 board for the Payments Team showing a realistic distribution of work items across five columns, including blocked items:_

```mermaid
kanban
    column1["📋 Backlog"]
        b1["📊 Add pool monitoring to auth"]
        b2["🔍 Evaluate PgBouncer"]
        b3["📝 Update runbook for pool alerts"]

    column2["🔧 In Progress"]
        ip1["📊 Build merchant dashboard MVP"]
        ip2["📚 Write v2 API migration guide"]
        ip3["🔐 Add OAuth2 PKCE flow"]

    column3["🔍 In Review"]
        r1["🛡️ Request validation middleware"]

    column4["🚫 Blocked"]
        bl1["🔄 Auth service pool config"]

    column5["✅ Done"]
        d1["🛡️ Rate limiting on /v2/charges"]
        d2["🐛 Fix pool exhaustion errors"]
        d3["📊 Pool utilization alerts"]
```

**Tips for complex kanban diagrams:**

- Add a **Blocked** column to surface stalled work — this is the highest-signal column on any board
- Keep items to **3–4 per column max** even in complex boards — the diagram is a summary, not an exhaustive list
- Use the **same emoji per domain** across columns for visual tracking (📊 = dashboards, 🛡️ = security, 🐛 = bugs)
