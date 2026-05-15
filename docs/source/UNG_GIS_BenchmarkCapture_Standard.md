---
title: "Survey Control & Benchmark Capture Standard"
author: "John Segars, MGIS"
organization: "University of North Georgia — Enterprise GIS Program, Facilities Planning"
division: "Facilities"
date: "April 2026"
version: "1.0"
classification: "Operational Reference"
---

# Survey Control & Benchmark Capture Standard

*GIS Division | Prepared by: John Segars, MGIS | April 2026 | Operational Reference*

---

## 1. Purpose

Construction drawings produced for UNG facilities projects contain embedded survey control information — benchmarks, iron pins, coordinate callouts, and pipe invert elevations — that represents professionally surveyed, legally defensible positional and vertical data. This information currently resides in archived PDFs and is effectively invisible to future GIS staff, contractors, and facilities planners.

This standard establishes what to capture, how to capture it, and why it matters for the long-term integrity of UNG's enterprise GIS program across all five campuses.

---

## 2. What to Capture

### 2.1 Survey Control Points and Benchmarks

Any drawing that includes explicit State Plane coordinates (Northing/Easting) or a NAVD 88 elevation tied to a physical monument should have that control point captured in GIS. Common forms include:

- **60D nails** driven into pavement, utility poles, or tree roots — temporary but coordinate-explicit
- **Iron pins** (set or found) at boundary corners — labeled IPS or IPF on drawings
- **Concrete monuments with brass disks** — permanent, highest reliability
- **NGS network monuments** — referenced by PID number, retrievable from the NGS datasheet database
- **Benchmark tie lines** — lines connecting the survey to an off-site control monument; follow the annotation to find the source coordinates

### 2.2 Pipe Infrastructure with Invert Elevations

Storm drainage, sanitary sewer, and culvert features shown with TOP / IN / OUT elevation callouts should be captured with those values as attributes. This data supports hydraulic analysis, ADA compliance review, and future construction planning.

- Corrugated metal pipe (CMP) — size, material, and invert elevations
- Reinforced concrete pipe (RCP) — same attribution
- PVC sanitary laterals and cleanouts
- Storm inlets and junction boxes with rim and invert elevations
- Headwalls and outfalls

### 2.3 Other High-Value Features

- Light pole bases — ground-level, discrete, useful for georeferencing future drawings
- Utility easement boundaries — legal constraint data
- Fire hydrants and water valves with size and material
- Gas line annotations with material and depth if shown
- Electrical and telecom duct banks — most frequently undocumented in GIS

---

## 3. Attribution Schema — Survey Control Feature Class

The recommended feature class is a point geometry type named `SurveyControl` or `BenchmarkControl` within the enterprise geodatabase.

| Field Name | Type | Description |
|---|---|---|
| MONUMENT_TYPE | Text (50) | 60D Nail, Iron Pin Set, Iron Pin Found, Concrete Monument, NGS Disk |
| NORTHING | Double | State Plane Georgia West Northing — from document, not digitized |
| EASTING | Double | State Plane Georgia West Easting — from document, not digitized |
| ELEVATION | Double | NAVD 88 elevation in feet — from document |
| VERT_DATUM | Text (20) | Vertical datum — typically NAVD 88 |
| SOURCE_DOC | Text (100) | Drawing title and project number (e.g., J425 GeoSurvey Site Survey) |
| SURVEY_FIRM | Text (100) | Surveying firm name (e.g., GeoSurvey, Marietta GA) |
| SURVEY_DATE | Date | Date of survey as shown on drawing |
| CAMPUS | Text (30) | Dahlonega, Gainesville, Cumming, Blue Ridge, Oconee |
| CONDITION | Text (30) | Reported / Verified Existing / Not Found / Destroyed |
| NOTES | Text (255) | Descriptive text from drawing; recovery notes if field verified |
| PDF_PATH | Text (255) | Network path or document management link to source PDF |
| ENTERED_BY | Text (50) | Staff member who entered the record |
| ENTERED_DATE | Date | Date of GIS entry |

---

## 4. How to Enter Control Points Correctly

> **Never digitize benchmark locations from a georeferenced image.** The georeferencing process introduces error that is larger than the precision the benchmark represents. Enter all control points using the coordinate values explicitly stated on the drawing.

**Workflow:**

1. Locate the Northing, Easting, and Elevation values in the drawing annotations or notes block.
2. In ArcGIS Pro, use **Map tab → Go To XY**. Enter Easting as X and Northing as Y. Confirm map CRS is set to **NAD 1983 StatePlane Georgia West FIPS 1002 (US Feet)**.
3. Flash the location to verify it lands in a logical position relative to the site.
4. Open the `SurveyControl` feature class in an edit session and create a new point at those exact coordinates using **Add XY** or direct coordinate entry — not by clicking the map.
5. Populate all attribution fields from the source document before closing the edit session.
6. Save the source PDF path in the `PDF_PATH` field and set `CONDITION` to `Reported`.

> **Note:** For NGS monuments referenced by PID, retrieve the full datasheet from [geodesy.noaa.gov/datasheets](https://geodesy.noaa.gov/datasheets) and use the published NAD 83 coordinates directly.

---

## 5. Long-Term Value

### 5.1 Georeferencing Future Drawings

A populated `SurveyControl` feature class becomes a campus-wide network of coordinate-explicit ground truth points. Future GIS staff georeferencing construction drawings can snap control points directly to verified benchmarks rather than hunting for features on an orthoimage. This eliminates the building-lean problem inherent in nadir orthophotos and dramatically reduces georeferencing error.

### 5.2 LIDAR Surface Validation

NAVD 88 benchmarks can be used to validate the vertical accuracy of LIDAR-derived surface models. Comparing benchmark elevations against the raster surface at those locations quantifies vertical error and informs confidence in slope, drainage, and ADA analysis derived from that surface.

### 5.3 Contractor Reference

Future contractors performing survey work on UNG campuses can use recovered benchmarks as starting control, reducing mobilization costs and ensuring new surveys tie to the same datum as existing campus data.

### 5.4 Institutional Memory

Construction activity is the primary destroyer of survey monuments. A GIS record with `CONDITION` tracking documents what existed, when it was verified, and what was lost to subsequent construction. This is institutional knowledge that currently exists nowhere in UNG's facilities documentation and will not be reconstructable once lost.

### 5.5 Program Continuity

A populated `SurveyControl` layer gives any GIS practitioner working with campus data immediate context for the spatial accuracy framework — what data was tied to survey control, what was digitized from georeferenced documents, and what the expected positional accuracy of each dataset is. This is foundational context that cannot be inferred from the geometry alone and benefits anyone working with the data regardless of how long they have been with the program.

---

## 6. Prioritization Guidance

Given the volume of archived construction drawings across five campuses, a systematic approach is necessary. Process drawings in the following priority order:

| Priority | Drawing Type / Criteria | Rationale |
|---|---|---|
| 1 — High | Boundary and topographic surveys, last 10 years | Most likely to have surviving monuments; highest coordinate precision |
| 2 — High | Active or planned construction sites | Control needed imminently for future georeferencing |
| 3 — Medium | Utility as-built drawings with invert elevations | Infrastructure data gap is highest here |
| 4 — Medium | Older surveys with NGS tie references | NGS monuments may still be recoverable and datasheets are available online |
| 5 — Low | Architectural drawings only | Little survey control content; prioritize other types first |

---

*This document was prepared by the UNG Enterprise GIS Program — Facilities Planning Division. Questions should be directed to the GIS Analyst / Facilities Planning Specialist. All coordinate values referenced in this standard use NAD 1983 StatePlane Georgia West FIPS 1002 (US Feet) horizontal datum and NAVD 88 vertical datum unless otherwise noted.*
