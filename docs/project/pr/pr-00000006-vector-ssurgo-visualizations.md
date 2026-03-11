# PR-00000006: Vector SSURGO Visualizations

| Field               | Value                                                               |
| ------------------- | ------------------------------------------------------------------- |
| **PR**              | [#6](https://github.com/SuperiorByteWorks-LLC/agent-project/pull/6) |
| **Author**          | Clayton Young ([@borealBytes](https://github.com/borealBytes))      |
| **Date**            | 2026-03-11                                                          |
| **Status**          | **In progress**                                                     |
| **Branch**          | `feat/vector-ssurgo-visualizations` → `main`                        |
| **Related issues**  | [#6](../issues/issue-00000006-vector-ssurgo-visualizations.md)      |
| **Deploy strategy** | TBD                                                                 |

---

## 📋 Summary

### What changed and why

Created vector SSURGO soil visualizations for Discovery Bay, CA (94514) area in the Sacramento-San Joaquin Delta region. Generated field boundary, soil polygons, buffer zones, and choropleth maps with ~60% transparency overlay layers.

Note: USDA SSURGO APIs were unavailable from this environment, so representative soil polygons based on actual Delta region soil series (Rindge, Canebrake, San Joaquin, etc.) were created for demonstration.

### Scope

- [x] Research SSURGO vector data format and structure
- [x] Design visualization approach for soil map units
- [x] Create field boundary for ~35 acre farm field
- [x] Generate soil polygon overlay with transparency
- [x] Create choropleth map by organic matter %
- [x] Add buffer zone (~60m ring)
- [x] Create soil properties data table
- [x] Combine into final panel visualization

### Status

**2026-03-11** — Completed: 4 maps + data table + final panel (3x2 grid). Files saved to data/.

---

## ✅ Validation Evidence

| Check    | Status     | Notes                                    |
| -------- | ---------- | ---------------------------------------- |
| Local CI | ⏳ Pending | Run `./scripts/ci-local.sh` before merge |
| Review   | ⏳ Pending | TBD                                      |

---

## 📦 Files Changed

_Track files modified in this PR._

| File                                   | Change                                     |
| -------------------------------------- | ------------------------------------------ |
| `data/ssurgo_visualization.py`         | Main visualization script                  |
| `data/field_boundary.geojson`          | Farm field boundary vector                 |
| `data/ssurgo_soils.geojson`            | Soil polygons (representative Delta soils) |
| `data/field_buffer.geojson`            | 60m buffer ring around field               |
| `data/ssurgo_field_visualizations.png` | 4-panel visualization grid                 |
| `data/ssurgo_final_panel.png`          | Final 3x2 panel with all maps + table      |
| `data/soil_properties_table.csv`       | Soil properties data                       |
| `data/soil_properties_table.png`       | Formatted table image                      |

---

## 🔗 Links

- [Branch](https://github.com/SuperiorByteWorks-LLC/agent-project/tree/feat/vector-ssurgo-visualizations)
- [Kanban board](../kanban/feature-vector-ssurgo-visualizations.md)
