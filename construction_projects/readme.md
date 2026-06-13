# construction_projects/

HTML map application for UNG Campus Construction Projects, embedded in the Hub experience.

**Hub experience:** [UNG Campus Construction Projects](https://experience.arcgis.com/experience/7b063270c2154678b98ea2b397584a0d)

---

## Files

| File | Description |
|------|-------------|
| [construction map HTML file] | Interactive map pulling live data from AGOL Construction Project Areas feature service |

---

## Update Workflow

1. Download the Facilities Project List Excel from SharePoint — save to `C:\Users\jdsegars\Downloads\Facilities Project List.xlsx`
2. In ArcGIS Pro open `Construction_Projects.aprx` → Analysis → Excel to Table with sheet `FN - Active`, range `A1:M100`
3. Close ArcGIS Pro
4. Run `Construction_Projects\Scripts\Create_Construction_Area_Polygons.py`
5. Reopen ArcGIS Pro → verify output → overwrite web layer **construction project areas** in the Public AGOL folder

> **If new buildings were added:** export a new `bldgs.csv` before running the script or new buildings will silently fail to appear.

---

*Full workflow documentation is in the internal repository under `docs/sops/`.*
