# UNG Facilities Planning & GIS — Pipeline Script Reference

**University of North Georgia | Facilities Planning & GIS**  
**Author:** John Segars, MGIS | jdsegars@ung.edu  
**Last Updated:** May 2026 | Internal Use

---

## Overview

This directory contains operational reference documentation for the AD → GIS Floor Plan Pipeline — an automated weekly workflow that parses Active Directory personnel location data and writes occupant information into GIS floor plan polygons across all five UNG campuses (Blue Ridge, Cumming, Dahlonega, Gainesville, Oconee).

Each document covers one script: what it does, what it needs, what it produces, and when to run it. Documents are provided in both `.docx` and `.pdf` format.

**May 21, 2026 pipeline results:** 2,458 AD accounts → 1,511 mappable → 1,150 GIS polygons populated → **76.2% placement rate**

---

## Weekly Pipeline — Run in This Order

| # | Document | Script | Version | Purpose |
|---|----------|--------|---------|---------|
| 1 | [01_AD_Parsing_V3.6](01_AD_Parsing_V3.6.pdf) | `AD_Parsing_V3.6.py` | V3.6 | Parses freeform AD location text into Building, Room, City |
| 2 | [02_CampusEmailLists](02_CampusEmailLists.pdf) | `CampusEmailLists.py` | V1.4 | Generates per-campus, per-building employee email lists |
| 3 | [03_AD_Delta_Comparison](03_AD_Delta_Comparison.pdf) | `AD_Delta_Comparison.py` | current | Tracks hires, departures, and office location changes since baseline |
| 4 | [04_Campus_Floor_Plans_ClearFields](04_Campus_Floor_Plans_ClearFields.pdf) | `Campus_Floor_Plans_ClearFields.py` | current | Blanks occupant fields across all feature classes before each run |
| 5 | [05_Campus_Floor_Plans_INFO_update_PROD_V3.5](05_Campus_Floor_Plans_INFO_update_PROD_V3.5.pdf) | `Campus_Floor_Plans_INFO_update_PROD_V3.5.py` | V3.5 | Writes AD occupant data into GIS polygons across all five campuses |
| 5b | [05b_Campus_Floor_Plans_INFO_update_TEST_V3.5](05b_Campus_Floor_Plans_INFO_update_TEST_V3.5.pdf) | `Campus_Floor_Plans_INFO_update_TEST_V3.5.py` | V3.5 | TEST version — run before PROD to verify results |
| 6 | [06_CampusFloorPlansMerge_V2.1](06_CampusFloorPlansMerge_V2.1.pdf) | `CampusFloorPlansMergeV2_1.py` | V2.1 | Merges five campus feature classes into enterprise TEMP.gdb |
| 7 | [07_FICM_CFP_PREP_V1.0](07_FICM_CFP_PREP_V1.0.pdf) | `FICM_CFP_PREP_V1.0.py` | V1.0 | Stages floor plan data for FICM-compliant export |
| 8 | [08_FloorPlanExporter_V2.5.0](08_FloorPlanExporter_V2.5.0.pdf) | `FloorPlanExporter_v2_5_0.py` | V2.5.0 | Exports 218 floor plan PDFs, 3 CSVs, and 5 campus workbooks |
| 9 | [09_Generate_Space_Reports_Standalone_V1.1](09_Generate_Space_Reports_Standalone_V1.1.pdf) | `Generate_Space_Reports_Standalone_v1_1.py` | V1.1 | Generates space reports without running the full PDF export |
| 10 | [10_Banner_Action_List_AllCampus_V4.4](10_Banner_Action_List_AllCampus_V4.4.pdf) | `Banner_Action_List_AllCampus.py` | V4.4 | Reconciles GIS space inventory against Banner FAC030 export |

---

## Setup & Maintenance Tools

Run once during initial setup, or when new buildings or departments appear in AD.

| # | Document | Script | Purpose |
|---|----------|--------|---------|
| 11 | [11_BuildingCrosswalk_Setup](11_BuildingCrosswalk_Setup.pdf) | `BuildingCrosswalk.py` | Builds the AD building name → GIS code crosswalk via fuzzy matching |
| 12 | [12_Department_to_Domain_CrosswalkV2_Setup](12_Department_to_Domain_CrosswalkV2_Setup.pdf) | `Department_to_Domain_CrosswalkV2.py` | Maps AD department names to COL_INS_CTR domain codes |

---

## On-Demand Diagnostic Tools

Run between pipeline cycles to investigate data quality issues or generate reporting.

| # | Document | Script | Purpose |
|---|----------|--------|---------|
| 13 | [13_AD_Lookup_Diagnostic_V1.0](13_AD_Lookup_Diagnostic_V1.0.pdf) | `AD_Lookup_Diagnostic_v1_0.py` | Classifies excluded AD records — no ArcGIS required |
| 14 | [14_Pipeline_Summary_Stats_V1.1](14_Pipeline_Summary_Stats_V1.1.pdf) | `Pipeline_Summary_Stats_v1_2.py` | Calculates briefing statistics and generates HTML summary and trend pages |
| 15 | [15_RoomNumberAnalysis_V4.0](15_RoomNumberAnalysis_V4.0.pdf) | `RoomNumberAnalysis.py` | Analyzes GIS room number quality — gaps, duplicates, floor counts |

---

## Key Data Files

| File | Purpose |
|------|---------|
| `Building_Crosswalk.xlsx` | 95 verified AD building name → GIS code mappings — read every run |
| `Department_to_Domain_CrosswalkV2.xlsx` | 108 department → COL_INS_CTR mappings — read every run |
| `FacStaffWithAddress_MMDDYYYY_parsed.xlsx` | Parsed AD output from Step 1 — input to Steps 2, 3, 5, 13, 14 |
| `Unmatched_AD_Rooms_TIMESTAMP.xlsx` | AD rooms not matched to a GIS polygon — includes Reason column (V3.4+) |
| `Excluded_AD_Records_TIMESTAMP.xlsx` | AD records dropped before matching — includes Reason column (V3.5+) |
| `pipeline_history.json` | Run history — appended by Pipeline_Summary_Stats on each run |
| `pipeline_summary.html` | Current run snapshot — copy to GitHub after each run |
| `pipeline_trend.html` | Multi-run trend page — copy to GitHub after each run |

---

## Pipeline Architecture

```
Active Directory Export (IT)
        │
        ▼
[1] AD_Parsing_V3.6          → FacStaffWithAddress_parsed.xlsx
        │
        ├──▶ [2] CampusEmailLists      → Campus_*.xlsx + Notification list → SharePoint
        │
        ├──▶ [3] AD_Delta_Comparison   → AD_Delta_TIMESTAMP.xlsx
        │
        ▼
[4] ClearFields              → OFF_ASGNE / asgn_to / Space_Info blanked
        │
        ▼
[5b] TEST Updater            → Verify against TEMP Campus_Floor_Plans
        │
        ▼
[5] PROD Updater V3.5        → 1,150 polygons populated across 5 campuses
        │                       Unmatched_AD_Rooms_TIMESTAMP.xlsx
        │                       Excluded_AD_Records_TIMESTAMP.xlsx
        ▼
[6] CampusFloorPlansMerge    → TEMP.gdb/Campus_Floor_Plans (8,436 records)
        │
        ▼
[7] FICM_CFP_PREP            → FMS.gdb/CFP_Floors + Campus_Floor_Plans
        │
        ▼
[8] FloorPlanExporter        → 218 PDFs + 3 CSVs + 5 XLSX → SharePoint
        │
        ▼
[9] Space Reports Standalone → CSVs + XLSX (when PDFs not needed)
        │
        ▼
[10] Banner Action List      → GIS vs Banner reconciliation workbooks
```

---

## The Blank-Slate Principle

Before each run, all occupant fields are cleared across all feature classes. This is intentional.

> *What you see populated = AD-confirmed today. What you see blank = unknown, unmaintained, or a GIS data gap. No ghosts.*

Active Directory is the system of record for personnel location. The pipeline is a mirror. Every percentage point above the current placement rate requires departments to maintain their employees' office locations in AD via EIS tools.

---

## Succession Notes

- **Banner space inventory access** must be a stated job requirement for the successor to this position — it is required for Banner Action List reconciliation (Step 10)
- **DEHYPHEN_BUILDINGS** (`DA008A`) appears in both PROD and TEST updater scripts — keep in sync; remove when AD entries for Hansford Hall are cleaned up
- **Building_Crosswalk.xlsx** is manually maintained — run the AD Lookup Diagnostic (Tool 13) periodically to identify new building names that need crosswalk entries
- The full pipeline runs as a push-button weekly operation; runtime approximately 30-35 minutes including PDF export

---

*UNG Facilities Planning & GIS | John Segars, MGIS | jdsegars@ung.edu*
