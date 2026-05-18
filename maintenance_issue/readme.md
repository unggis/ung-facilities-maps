# Facilities Issue Map

**Project:** UNG Facilities Issue Map
**Status:** Beta — internal testing
**Location:** `ung-facilities-internal/projects/facilities-issue-map/`
**Owner:** John Segars, GIS Analyst / Facilities Planning Specialist
**Last updated:** May 2026

---

## What This Is

A Leaflet web map that displays non-emergency facilities issue reports submitted via the UNG Facilities Issue Reporting Survey123 form. Intended for internal Facilities staff use — linked from Power Automate email notifications so the recipient can see exactly where a reported issue is located on campus.

The map pulls live from the Survey123 feature layer via AGOL. No data file to maintain — submissions appear automatically as they are received.

---

## How It Works

1. Someone scans a QR code at a campus location and taps "Report a Facilities Issue"
2. They complete the Survey123 form and submit
3. The Survey123 webhook fires, sending the submission to Power Automate
4. Power Automate sends an email notification to the designated Facilities recipient
5. The email includes a link to this map with the submission's objectid as a URL parameter
6. The recipient clicks the link — the map opens, flies to the reported location, highlights the marker, and opens the popup

---

## URL Structure

### Specific submission (from email link)
```
https://unggis.github.io/ung-facilities-maps/issues/?oid=9
```
Flies to that submission, highlights it with an amber pulsing marker, opens popup automatically.

### All submissions (overview)
```
https://unggis.github.io/ung-facilities-maps/issues/
```
Shows all current submissions across all five campuses. Defaults to all-campus zoom.

### Coordinate fallback (if OID not available)
```
https://unggis.github.io/ung-facilities-maps/issues/?x=-83.86871588&y=34.233672843
```
Flies to coordinates without highlighting a specific marker.

---

## Data Source

**Feature service (view — public):**
```
https://services3.arcgis.com/4ADpogqF2B4hadEB/arcgis/rest/services/Non-emergency_maintenance_items_VIEW/FeatureServer/0
```

**Fields used:**
| Field | Label | Notes |
|---|---|---|
| `field_10` | Campus | e.g. "Dahlonega Campus" |
| `type_of_issue_being_reported` | Issue Type | Landscape, Roads, Safety, etc. |
| `describe_the_issue_along_with_i` | Description | Free text from submitter |
| `objectid` | Record ID | Used for URL parameter routing |

**Fields intentionally excluded:**
- `contact_information` — submitter email, kept private via the view layer
- `globalid` — internal identifier, not needed for display

---

## Power Automate Integration

### Email body dynamic link

In the Power Automate "Send an email" step, add this line to the body:

```
View on map: https://unggis.github.io/ung-facilities-maps/issues/?oid=[objectid]
```

Replace `[objectid]` with the dynamic content field from the HTTP trigger payload.

### Full recommended email body

```
New Facilities Issue Reported

Campus:       [field_10]
Issue Type:   [type_of_issue_being_reported]
Description:  [describe_the_issue_along_with_i]
Contact:      [contact_information]
Submitted by: [fullName]

View on map: https://unggis.github.io/ung-facilities-maps/issues/?oid=[objectid]

Log in to Survey123 to view attached photos:
https://survey123.arcgis.com/surveys/ca742b0a3514485fa625475ccbc314e4/data
```

---

## Issue Type Icons

| Icon | Type |
|---|---|
| 🌿 | Landscape |
| 🛣 | Roads |
| ⚠️ | Safety |
| 🪧 | Signage |
| 🐾 | Wildlife |
| ⚡ | Electrical |
| 🔧 | Plumbing |
| 💡 | Lighting |
| 🗑 | Trash |
| 📍 | Other / default |
| 📍 amber | Currently highlighted submission |

To add a new issue type — add an entry to the `ISSUE_ICONS` object in `app/index.html` and a corresponding legend item in the legend HTML block.

---

## File Structure

```
facilities-issue-map/
├── docs/
│   └── README.md          ← this file
└── app/
    └── index.html         ← the map application
```

---

## Deployment

When ready to promote to the public repo:

1. Copy `app/index.html` to `ung-facilities-maps/issues/index.html`
2. Push to `ung-facilities-maps` public repo
3. Confirm GitHub Pages serves it at `unggis.github.io/ung-facilities-maps/issues/`
4. Update Power Automate email body with the live URL
5. Test end to end — submit a form, confirm email arrives with working map link

**Note:** The map is labeled "Internal" in the header badge. This is a visual indicator only — the page itself is publicly accessible once deployed to GitHub Pages. The data displayed is already public via the AGOL view layer. Contact information is not exposed.

---

## Known Limitations

- No date/time field currently exposed in the view layer. If submission timestamp is needed, the AGOL view may need to be updated to include `CreationDate`
- Photo attachments are not displayed in the map popup — submitter photos must be viewed directly in Survey123
- Issue type icons depend on exact string matching — if Survey123 form choices change, icon mappings in `ISSUE_ICONS` must be updated to match
- The AGOL view layer sharing must remain set to "Everyone (public)" for the map to load without authentication

---

## Related Projects

| Project | Location | Notes |
|---|---|---|
| Campus Waypoint Map | `ung-facilities-maps/waypoints/` | Public — QR code wayfinding |
| Campus Vision Plan | `ung-facilities-maps/` | Public — existing vs proposed buildout |
| Facilities GIS Hub | gis-ung-facilities.hub.arcgis.com | Public portal |
| Survey123 Form | survey123.arcgis.com/surveys/ca742b0a3514485fa625475ccbc314e4 | Public submission form |

---

## Contact

John Segars, MGIS
GIS Analyst / Facilities Planning Specialist
University of North Georgia — Facilities Management
jdsegars@ung.edu
