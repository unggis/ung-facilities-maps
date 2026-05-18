# Facilities Issue Map

**Project:** UNG Facilities Issue Map
**Status:** Beta — working concept, internal use
**Location:** `ung-facilities-internal/projects/facilities-issue-map/`
**Owner:** John Segars, GIS Analyst / Facilities Planning Specialist
**Last updated:** May 2026

---

## What This Is

A Leaflet web map that displays non-emergency facilities issue reports submitted via the UNG Facilities Issue Reporting Survey123 form. Intended for internal Facilities staff use — linked from Power Automate email notifications so the recipient can see exactly where a reported issue is located on campus, view the description, and see any attached photos.

The map pulls live from the Survey123 feature layer via AGOL. No data file to maintain — submissions appear automatically as they are received. Only records with `Status = Open` are displayed. Resolved issues are hidden automatically.

---

## The Full Pipeline

```
User scans QR code on campus
        ↓
Taps "Report a Facilities Issue" → Survey123 form
        ↓
Submits form (description, issue type, campus, photo)
        ↓
Survey123 webhook fires → Power Automate
        ↓
Email notification sent to Facilities staff
        ↓
Staff clicks map link in email → Facilities Issue Map
        ↓
Map flies to reported location, popup opens
        ↓
Staff views description + photo in popup
        ↓
Issue resolved in field → Staff marks Resolved in AGOL
        ↓
Record disappears from map on next load/refresh
```

---

## How to Use the Map

### Viewing issues
- Open the map — all Open issues load automatically across all campuses
- Click campus buttons in toolbar to fly to a specific campus
- Click any marker to open the popup — shows issue type, record ID, campus, date reported, description, and photos
- Click a photo thumbnail to view full size — press Escape or click anywhere to close
- Click **Refresh** in toolbar to reload live data without refreshing the page

### From an email notification
The Power Automate notification email includes a direct link:
```
https://unggis.github.io/ung-facilities-maps/maintenance_issue/?oid=[objectid]
```
Clicking this link opens the map already centered on the reported location with the popup open.

---

## Marking an Issue as Resolved

**Current workflow — AGOL data tab:**

1. Note the **Record ID** from the email notification or map popup
2. Log into **ung-facilities.maps.arcgis.com** with your UNG credentials
3. Go to **Content** → find **UNG Facilities Issue Reporting** (the master hosted feature layer — not the view)
4. Click **Data** tab
5. Find the record by objectid
6. Click the record to edit it
7. Change **Status** from `Open` to `Resolved`
8. Save

The record will no longer appear on the map after the next load or Refresh.

**Alternative — Survey123 data tab:**

1. Go to **survey123.arcgis.com**
2. Open **UNG Facilities Issue Reporting**
3. Click **Data** tab
4. Find the record
5. Click the edit (pencil) icon
6. Change Status to `Resolved`
7. Save

---

## Issue Types & Icons

| Icon | Type |
|---|---|
| 🌿 | Landscape |
| 💡 | Lighting |
| 🛣 | Roads |
| ⚠️ | Safety |
| 🚶 | Sidewalks |
| 🪧 | Signage |
| 🗑 | Waste |
| 🐾 | Wildlife |
| 📍 | Other |
| 📍 amber/pulsing | Currently highlighted submission (from email link) |

---

## Data Source

**Feature service view (public):**
```
https://services3.arcgis.com/4ADpogqF2B4hadEB/arcgis/rest/services/Non-emergency_maintenance_items_VIEW/FeatureServer/0
```

**Query filter:** `Status = 'Open'`

**Fields used:**

| Field | Label | Notes |
|---|---|---|
| `field_10` | Campus | e.g. "Dahlonega Campus" |
| `type_of_issue_being_reported` | Issue Type | Landscape, Roads, Safety, etc. |
| `describe_the_issue_along_with_i` | Description | Free text from submitter |
| `objectid` | Record ID | Used for URL parameter routing |
| `CreationDate` | Date reported | Displayed in popup |
| `Status` | Open / Resolved | Used to filter map display |

**Fields intentionally excluded:**
- `contact_information` — submitter email, kept private via the view layer

**Important:** The view layer must remain shared to **Everyone (public)** in AGOL for the map to load. Editing the view's fields can reset sharing — verify after any view changes.

---

## URL Structure

| Mode | URL | Behavior |
|---|---|---|
| All open issues | `unggis.github.io/ung-facilities-maps/maintenance_issue/` | Shows all Open records, all-campus zoom |
| Specific submission | `unggis.github.io/ung-facilities-maps/maintenance_issue/?oid=12` | Flies to that record, highlights marker, opens popup |
| Coordinate fallback | `unggis.github.io/ung-facilities-maps/maintenance_issue/?x=-83.86&y=34.23` | Flies to coordinates |

---

## Power Automate Email Integration

**Flow name:** Survey123 Action Item
**Trigger:** HTTP webhook from Survey123 — fires on new submission
**Action:** Send an email (V2) via Outlook to designated Facilities recipient

**Recommended email body:**
```
New Facilities Issue Reported

Campus:       [field_10]
Issue Type:   [type_of_issue_being_reported]
Description:  [describe_the_issue_along_with_i]
Contact:      [contact_information]
Submitted by: [fullName]

View on map:
https://unggis.github.io/ung-facilities-maps/maintenance_issue/?oid=[objectid]

View full submission and photos in Survey123:
https://survey123.arcgis.com/surveys/ca742b0a3514485fa625475ccbc314e4/data
```

**Note:** The Power Automate connection uses `jdsegars@ung.edu` credentials. If the flow stops working, reauthenticate the Outlook connection at flow.microsoft.com. This may be required after password changes or MFA policy updates.

---

## Known Limitations

**Resolve workflow requires AGOL login**
There is no one-click resolve button in the map — resolving an issue requires logging into AGOL or Survey123 and editing the record manually. See Future Improvements below.

**Photo attachments require AGOL public access**
Photos are fetched directly from the AGOL feature service. If the view layer sharing is changed from public, photos will fail to load.

**Cache behavior**
AGOL caches query results aggressively. The app appends `Date.now()` to every query to force fresh results. If resolved issues still appear after refresh, wait 30-60 seconds and refresh again.

**No date filter**
The map shows all Open issues regardless of age. Old unresolved issues will accumulate unless marked Resolved in AGOL.

**Status field is case sensitive**
The query filters on `Status = 'Open'` exactly. Ensure consistent capitalization when editing records — `open` or `OPEN` will not match.

---

## Future Improvements

### One-Click Resolve (Priority)
Add a "Mark Resolved" button to each popup that updates the Status field directly from the map. Requires AGOL OAuth authentication — staff log in once via a login button in the app header, then resolve issues with one tap.

**Technical approach:** AGOL OAuth 2.0 → token stored in session → `applyEdits` POST to feature service with `Status = 'Resolved'` for that objectid.

### Date Filter
Add a toolbar control to filter issues by date range — Last 7 days, Last 30 days, All. Useful as submission volume grows.

### Campus-Filtered View
Clicking a campus button currently flies the map but still shows all markers. A true filter would show only markers for the selected campus.

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

## Deployment Checklist

When ready to promote to the public repo:

- [ ] Verify AGOL view layer is shared to Everyone (public)
- [ ] Test query URL returns only Open records
- [ ] Test email link `?oid=X` flies to correct marker
- [ ] Test photo loads in popup lightbox
- [ ] Test Refresh button clears resolved records
- [ ] Copy `app/index.html` to `ung-facilities-maps/maintenance_issue/index.html`
- [ ] Push to `ung-facilities-maps` public repo
- [ ] Confirm live at `unggis.github.io/ung-facilities-maps/maintenance_issue/`
- [ ] Update Power Automate email body with live map link
- [ ] Designate Facilities staff recipient for email notifications
- [ ] Document resolve workflow for that recipient

---

## Related Projects & Links

| Item | Location |
|---|---|
| Campus Waypoint Map | `unggis.github.io/ung-facilities-maps/waypoints/` |
| Survey123 Report Form | `survey123.arcgis.com/surveys/ca742b0a3514485fa625475ccbc314e4` |
| AGOL Feature Layer (master) | ung-facilities.maps.arcgis.com → Content → UNG Facilities Issue Reporting |
| AGOL Feature Layer (view) | ung-facilities.maps.arcgis.com → Content → Non-emergency_maintenance_items_VIEW |
| Power Automate Flow | flow.microsoft.com → Survey123 Action Item |
| Facilities GIS Hub | gis-ung-facilities.hub.arcgis.com |

---

## Contact

John Segars, MGIS
GIS Analyst / Facilities Planning Specialist
University of North Georgia — Facilities Management
jdsegars@ung.edu
