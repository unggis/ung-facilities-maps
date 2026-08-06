# SF Alignment — Banner ↔ GIS Reconciliation

**Live dashboard:** https://unggis.github.io/ung-facilities-maps/alignment_banner-gis/

Tracks how closely UNG's GIS floor plans agree with Banner's registrar records across all five campuses — building by building, and by total square footage.

## What it measures

| Metric | What it means |
|---|---|
| **SF Alignment** | Share of total GIS room square footage that matches Banner's reported square footage for the same rooms. Weighted by area, so a handful of large buildings dominate the number. |
| **Building Score** | Share of in-scope buildings with zero open ADD / REMOVE / UPDATE actions — the plainer, unweighted count. |

A few categories are handled specially before either score is calculated:

- **Known noise** — buildings with symmetric ADD/REMOVE counts traced to a room-numbering convention mismatch rather than a real discrepancy; excluded until resolved.
- **Banner-only** — buildings with no GIS polygon and only REMOVE actions, almost always a retired building still carried in Banner.
- **Institutional splits** — buildings where GIS and Banner deliberately code the same physical space differently (e.g. Cumming's J378/UC0124 pairing); both sides count as clean.

## Files in this folder

| File | Purpose |
|---|---|
| `index.html` | The dashboard itself. Reads `GIS_Banner_Alignment_History.csv` at page load — no build step, no server-side rendering. |
| `GIS_Banner_Alignment_History.csv` | One row per run: enterprise and per-campus SF Alignment %, Building Score %, action counts, and duplicate-room counts. |

## How it's generated

Updated by a local script (`GIS_Banner_Alignment_Check.py`) that reads the current Banner Action List workbooks, scores every building, and appends a row to the history CSV. A companion script (`GIS_Banner_Alignment_Publish.py`) runs that check and pushes the updated CSV — and, if it's changed, this HTML — to this folder.

Companion to [`/ad_gis_pipeline`](../ad_gis_pipeline/) in this repo, which tracks whether *people* are mapped to the right room. This folder tracks whether the *room itself* is described the same way in both systems.

---
UNG Facilities Planning & GIS
