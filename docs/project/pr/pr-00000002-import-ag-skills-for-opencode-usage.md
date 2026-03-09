# PR-00000002: Import ag-skills for OpenCode Usage

| Field               | Value                                                               |
| ------------------- | ------------------------------------------------------------------- |
| **PR**              | [#2](https://github.com/SuperiorByteWorks-LLC/agent-project/pull/2) |
| **Author**          | Clayton Young ([@borealBytes](https://github.com/borealBytes))      |
| **Date**            | 2026-03-09                                                          |
| **Status**          | **Ready to merge** — awaiting GitHub merge                          |
| **Branch**          | `skills-import` → `main`                                            |
| **Related issues**  | None                                                                |
| **Deploy strategy** | **No deploy** — local-only OpenCode skill configuration             |

---

## Summary

### What changed and why

This PR imports agricultural data analysis skills from the external [borealBytes/ag-skills](https://github.com/borealBytes/ag-skills) repository into the project's `.opencode/skills/` directory, making them available for OpenCode's native skill tool.

The skills enable AI agents to work with US agricultural data including field boundaries, soil data, weather data, satellite imagery, and crop classifications using standard Python libraries.

### Skills imported

| Skill                 | Description                          | Source                                                                                        |
| --------------------- | ------------------------------------ | --------------------------------------------------------------------------------------------- |
| `field-boundaries`    | USDA NASS Crop Sequence Boundaries   | [ag-skills](https://github.com/borealBytes/ag-skills/tree/skills-content/field-boundaries)    |
| `ssurgo-soil`         | USDA NRCS SSURGO soil data           | [ag-skills](https://github.com/borealBytes/ag-skills/tree/skills-content/ssurgo-soil)         |
| `nasa-power-weather`  | NASA POWER weather data              | [ag-skills](https://github.com/borealBytes/ag-skills/tree/skills-content/nasa-power-weather)  |
| `cdl-cropland`        | USDA NASS Cropland Data Layer        | [ag-skills](https://github.com/borealBytes/ag-skills/tree/skills-content/cdl-cropland)        |
| `sentinel2-imagery`   | ESA Sentinel-2 satellite imagery     | [ag-skills](https://github.com/borealBytes/ag-skills/tree/skills-content/sentinel2-imagery)   |
| `landsat-imagery`     | USGS Landsat satellite imagery       | [ag-skills](https://github.com/borealBytes/ag-skills/tree/skills-content/landsat-imagery)     |
| `interactive-web-map` | Interactive web maps with Leaflet.js | [ag-skills](https://github.com/borealBytes/ag-skills/tree/skills-content/interactive-web-map) |

### Key adaptations

- Added `license: MIT` (per source repository)
- Added `compatibility: opencode` for OpenCode skill discovery
- Converted folder names to hyphen format (OpenCode requirement: `field_boundaries` → `field-boundaries`)
- Updated internal references in skill content to reflect new paths
- Included example data for `field-boundaries` and `ssurgo-soil` skills

### Verification

OpenCode automatically discovers skills in `.opencode/skills/<name>/SKILL.md`. Each skill includes:

- YAML frontmatter with `name`, `description`, `license`, `compatibility`, and `metadata`
- Full skill documentation with usage examples
- Prerequisites and installation instructions
- Python API references

---

## Impact classification

| Dimension         | Level             | Notes                                                                   |
| ----------------- | ----------------- | ----------------------------------------------------------------------- |
| **Risk**          | 🟢 Low            | Documentation and config only; no production code or deployment changes |
| **Scope**         | Narrow            | 9 new files in `.opencode/skills/`                                      |
| **Reversibility** | Easily reversible | Revert commit removes all new files                                     |
| **Security**      | None              | No credentials or secrets; skills use public USDA/NASA APIs             |

---

## Merge readiness

**Status:** ✅ Ready to merge

OpenCode will automatically load these skills when the agent uses the `skill` tool. No additional configuration required.

---

## Changes

| File / Area                                                          | Change type | Description                               |
| -------------------------------------------------------------------- | ----------- | ----------------------------------------- |
| `.opencode/skills/field-boundaries/SKILL.md`                         | Added       | USDA NASS Crop Sequence Boundaries skill  |
| `.opencode/skills/field-boundaries/examples/sample_2_fields.geojson` | Added       | Example field boundary data (2 MN fields) |
| `.opencode/skills/ssurgo-soil/SKILL.md`                              | Added       | USDA NRCS SSURGO soil data skill          |
| `.opencode/skills/ssurgo-soil/examples/soil_data_2_fields.csv`       | Added       | Example soil data for 2 fields            |
| `.opencode/skills/nasa-power-weather/SKILL.md`                       | Added       | NASA POWER weather data skill             |
| `.opencode/skills/cdl-cropland/SKILL.md`                             | Added       | USDA NASS Cropland Data Layer skill       |
| `.opencode/skills/sentinel2-imagery/SKILL.md`                        | Added       | ESA Sentinel-2 imagery skill              |
| `.opencode/skills/landsat-imagery/SKILL.md`                          | Added       | USGS Landsat imagery skill                |
| `.opencode/skills/interactive-web-map/SKILL.md`                      | Added       | Interactive web maps skill                |

---

## Architecture impact

This change adds OpenCode agent skills but does not modify product runtime architecture.

```mermaid
flowchart LR
    accTitle: OpenCode Skill Discovery
    accDescr: How OpenCode discovers and loads skills from the project

    repo[📂 Repository] -->|scans| opencode[.opencode/skills/]
    opencode -->|finds| skill[📄 SKILL.md]
    skill -->|loads| tool[🛠️ skill tool]
    tool -->|provides| agent[🤖 AI Agent]

    classDef primary fill:#e0e7ff,stroke:#4f46e5,stroke-width:2px,color:#1e1b4b
    classDef success fill:#dcfce7,stroke:#16a34a,stroke-width:2px,color:#14532d

    class repo,opencode primary
    class skill,tool,agent success
```

---

## Testing

### How to verify

1. Open OpenCode in the project
2. Use the `skill` tool to list available skills
3. Confirm all 7 agricultural skills appear in the available skills list
4. Test loading a skill: `skill({ name: "field-boundaries" })`

### Expected output

```
<available_skills>
  <skill>
    <name>field-boundaries</name>
    <description>Download USDA NASS Crop Sequence Boundaries for agricultural fields...</description>
  </skill>
  <skill>
    <name>ssurgo-soil</name>
    <description>Download USDA NRCS SSURGO soil data for agricultural fields</description>
  </skill>
  ...
</available_skills>
```
