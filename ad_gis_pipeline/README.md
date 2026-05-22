# UNG Facilities GIS — Pipeline Statistics

**University of North Georgia | Facilities Planning & GIS**  
**Author:** John Segars, MGIS | jdsegars@ung.edu  
**Repository:** unggis (public) | `ad_gis_pipeline/` directory  
**Last Updated:** May 2026

---

## What This Directory Contains

Three files that together provide a live, publicly accessible view of the AD → GIS Floor Plan Pipeline — the automated weekly workflow that maps UNG employee office locations into GIS floor plan polygons across all five campuses.

| File | Purpose | Updated |
|------|---------|---------|
| `index.html` | Current run snapshot — six summary statistics | Weekly |
| `trend.html` | Multi-run trend page — placement rate and gap history | Weekly |
| `pipeline_history.json` | Raw data powering trend.html | Weekly |

These files are generated automatically by `Pipeline_Summary_Stats_v1_2.py` and pushed here after each weekly pipeline run. No server required — all three are self-contained static files.

---

## Viewing the Pages

| Page | URL |
|------|-----|
| Current run snapshot | `https://unggis.github.io/ad_gis_pipeline/` |
| Trend / history | `https://unggis.github.io/ad_gis_pipeline/trend.html` |

Both pages are self-contained — no build step, no server, no external data calls beyond Google Fonts and Chart.js from CDN.

---

## index.html — Current Run Snapshot

Shows the six statistics from the most recent pipeline run:

- **Total AD Accounts** — full UNG workforce in Active Directory
- **Mappable Records** — accounts with complete Building + Room + City in AD
- **GIS Polygons Populated** — room polygons with a confirmed occupant today
- **Placement Rate** — GIS Populated ÷ Mappable (goal: 100%)
- **Campuses Live** — always 5 (BRC, CC, DC, GC, OC)
- **Gap Records** — mappable records not placed on a polygon, with breakdown by reason

Also includes the population breakdown table (how the 2,458 total AD accounts reduce to the 1,511 mappable population), the gap breakdown table (no_match vs duplicates), and the full 10-step pipeline description.

Placement rate box color is dynamic: **green ≥ 80%**, **amber ≥ 65%**, **red < 65%**.

---

## trend.html — Multi-Run History

Shows pipeline performance across all recorded runs:

- **Goal hero** — current placement rate with a progress bar toward 100%, week-over-week delta
- **Placement Rate line chart** — y-axis floored dynamically so week-over-week movement is visible; 100% goal line shown as dashed green
- **Gap trend line chart** — No Match (amber) and Duplicates (red dashed) as separate lines over time; y-axis zoomed to actual gap range
- **Gap breakdown boxes** — current no_match, duplicates, and polygons remaining to goal with delta vs previous run
- **Runs table** — all recorded runs, latest first, with ↑↓ delta arrows on every column

The two gap lines tell different stories:
- **No Match** drops as crosswalk entries are added and AD data quality improves — this is the actionable line
- **Duplicates** stays flat until the 78 duplicate Dahlonega polygons are resolved in GIS

---

## pipeline_history.json — Run Data

One record per pipeline run, appended automatically by `Pipeline_Summary_Stats_v1_2.py`. The trend page reads this file directly — adding a new run and pushing the updated JSON is all that's needed to update the chart.

```json
{
  "run_date":        "2026-05-21",
  "run_label":       "May 21, 2026",
  "total_ad":        2458,
  "mappable":        1511,
  "suspect":         712,
  "online_blank":    209,
  "missing_location": 26,
  "gis_populated":   1150,
  "placement_rate":  76.2,
  "gap_no_match":    83,
  "gap_duplicates":  78
}
```

Records are deduplicated by `run_label` — re-running the script on the same day overwrites rather than appending a duplicate entry. Sorted chronologically.

**Current history:** 5 runs recorded (March 19 – May 21, 2026)

---

## How It Gets Updated

After each weekly pipeline run:

1. Run `Pipeline_Summary_Stats_v1_2.py` from `ActiveDirectoryParsing\` with the matched file pair:
   - `PARSED_AD_FILE` → `FacStaffWithAddress_MMDDYYYY_parsed.xlsx`
   - `UNMATCHED_FILE` → `Unmatched_AD_Rooms_TIMESTAMP.xlsx`

2. Three files are written automatically to `ActiveDirectoryParsing\`:
   - `pipeline_summary.html`
   - `pipeline_trend.html`
   - `pipeline_history.json` (appended)

3. Copy and rename to this directory:
   ```
   pipeline_summary.html  →  ad_gis_pipeline/index.html
   pipeline_trend.html    →  ad_gis_pipeline/trend.html
   pipeline_history.json  →  ad_gis_pipeline/pipeline_history.json
   ```

4. Commit and push:
   ```
   git add ad_gis_pipeline/
   git commit -m "Pipeline run MMDDYYYY — XX.X% placement rate"
   git push
   ```

Pages are live immediately after push (GitHub Pages, no build step).

---

## Script Configuration

`Pipeline_Summary_Stats_v1_2.py` — key config variables:

```python
PARSED_AD_FILE    = r"C:\...\FacStaffWithAddress_MMDDYYYY_parsed.xlsx"
UNMATCHED_FILE    = r"C:\...\Unmatched_AD_Rooms_TIMESTAMP.xlsx"
HTML_OUTPUT_FILE  = r"C:\...\pipeline_summary.html"
HISTORY_JSON_FILE = r"C:\...\pipeline_history.json"
TREND_HTML_FILE   = r"C:\...\pipeline_trend.html"
```

Update `PARSED_AD_FILE` and `UNMATCHED_FILE` for each run. All other paths are stable.

**Requirements:** Python with pandas. No ArcGIS required.  
**Requires Updater V3.4+** for full gap breakdown (Reason column in unmatched file). Pre-V3.4 files trigger a warning and fall back to total-only gap reporting.

---

## Understanding the Numbers

**Why 76.2% and not higher:**  
The placement rate denominator is the *mappable* population — 1,511 people whose AD entries have a complete Building + Room + City. The remaining 947 accounts are excluded before matching for legitimate reasons: 712 flagged Suspect (part-time, adjunct, trades, police with no fixed office), 209 Online/blank/No Office, 26 missing location data.

**What moves the placement rate:**  
- Departments maintaining employee office locations in AD via EIS tools
- Crosswalk additions resolving the no_match bucket (83 records)
- Fixing the 78 duplicate Dahlonega polygons in GIS

**What doesn't move it:**  
The pipeline itself is working correctly. A blank room on the floor plan is an honest answer — it means AD doesn't confirm an occupant today, not that the room is empty.

---

## Gap Breakdown — May 21, 2026

| Category | Count | Cause | Fix |
|----------|-------|-------|-----|
| No matching GIS polygon | 83 | AD room entry exists but GIS has no polygon at that building+room | Crosswalk additions; AD entry corrections |
| Duplicate polygons skipped | 78 | Ambiguous building+room combinations in Dahlonega — updater skips to prevent wrong writes | Resolve duplicate polygons in DC_FLOORPLANS |
| Excluded before matching | ~263 | Building not in crosswalk (~234), room blank in AD (~29) | Crosswalk additions; AD data quality |

---

*UNG Facilities Planning & GIS | John Segars, MGIS | jdsegars@ung.edu*  
*Generated by Pipeline_Summary_Stats_v1_2.py | pipeline_history.json | May 2026*
