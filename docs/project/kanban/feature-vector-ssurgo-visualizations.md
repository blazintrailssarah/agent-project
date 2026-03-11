# Feature: Vector SSURGO Visualizations — Kanban Board

_Feature: Vector SSURGO Visualizations · Started: 2026-03-11_
_Last updated: 2026-03-11 (initial visualization complete)_

---

## 📋 Board Overview

**Goal:** Implement vector-based SSURGO data visualizations
**WIP Limit:** 3 items In Progress

### Visual board

```mermaid
kanban
Backlog
In Progress
  task1["🗺️ Create field boundary + basemap"]
  task2["🗺️ Create SSURGO soil overlay (60% transparency)"]
  task3["🗺️ Create choropleth map (Organic Matter %)"]
  task4["🗺️ Create buffer zone (~60m ring)"]
  task5["📊 Create soil properties table"]
  task6["🖼️ Create final panel (3x2 grid)"]
In Review
Done
  task7["✅ Research: SSURGO format and libraries"]
  task8["✅ Design: Visualization architecture"]
  task9["✅ Environment: Python + geopandas + matplotlib"]
Blocked
Won't Do
```

> ⚠️ **Always show all 6 columns** — Even if a column has no items, include it with a placeholder.

---

## 🚦 Board Status

| Column             | Count | WIP Limit | Status                        |
| ------------------ | ----- | --------- | ----------------------------- |
| 📋 **Backlog**     | 0     | —         | —                             |
| 🔄 **In Progress** | 6     | 3         | 🔶 Visualizations in progress |
| 🔍 **In Review**   | 0     | —         | —                             |
| ✅ **Done**        | 3     | —         | Research + design complete    |
| 🚫 **Blocked**     | 0     | —         | Clear                         |

---

## 📝 Notes

_Research phase: Evaluate D3.js, Leaflet, deck.gl, and Mapbox GL JS for vector tile rendering._

---

## 🔗 Links

- [PR #6](../pr/pr-00000006-vector-ssurgo-visualizations.md)
- [Issue #6](../issues/issue-00000006-vector-ssurgo-visualizations.md)
