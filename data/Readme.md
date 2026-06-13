# data/

GeoJSON data files consumed by the HTML map applications in `../html/`.

## Files

| File | Used By | Description |
|------|---------|-------------|
| MPBUILDINGSOUTjson.geojson | ung-masterplan-swipe.html | Existing campus building footprints — all five campuses |
| MPVISIONjson.geojson | ung-masterplan-swipe.html | Proposed master plan features — 2035 buildout |
| ServiceGridOUTjson.geojson | walkway.html | Walkway of Service brick grid — Dahlonega Campus |

## Notes

These files are fetched by the HTML applications using `raw.githubusercontent.com` URLs:
`https://raw.githubusercontent.com/unggis/ung-facilities-maps/main/data/[filename]`

**Do not rename files without updating the corresponding fetch URL inside the HTML file.**
See `../html/` for which file references which GeoJSON.

When updating a GeoJSON file with new data, replace the file in place —
same filename — to avoid breaking existing fetch references.

## Source

GeoJSON files are exported from ArcGIS Pro using the enterprise GDB.
Contact the GIS Analyst / Facilities Planning Specialist for the export workflow.
