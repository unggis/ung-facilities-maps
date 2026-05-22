"""
Pipeline Summary Stats V1.2
----------------------------
Reads the parsed AD Excel file and the Unmatched_AD_Rooms Excel file
from a given pipeline run and calculates the six summary statistics
shown in the Pre-Meeting Briefing:

  1. Total AD Accounts
  2. Mappable Records (complete Building + Room + City)
  3. GIS Polygons Populated
  4. Placement Rate
  5. Campuses Live (always 5 — static)
  6. Gap Records

Also breaks down the gap into:
  - Duplicate polygon skips (Reason = 'duplicate')
  - AD entries with no matching GIS polygon (Reason = 'no_match')

CHANGES IN V1.2:
  - Added pipeline_history.json append on each run. One record per run,
    deduplicated by run_label so re-running the same day overwrites rather
    than duplicating. Copy JSON to GitHub after each run.
  - Added pipeline_trend.html generation from pipeline_trend_template.html.
    The trend page shows placement rate over time, stacked bar chart of
    populated vs gap breakdown, delta arrows in the runs table, and the
    remaining-to-goal count. Requires pipeline_trend_template.html in the
    same folder as this script.
  - Three GitHub files to keep in sync after each run:
      pipeline_summary.html   — current run snapshot
      pipeline_trend.html     — multi-run trend page
      pipeline_history.json   — raw data powering the trend page

CHANGES IN V1.1:
  - Reads Reason column from unmatched file (added in updater V3.4).
    GIS Polygons Populated is now derived as:
      Mappable - no_match - duplicates
    rather than Mappable - total gap, which was inaccurate because
    duplicates were counted in gap_total but not actually mappable.
  - Gap Records now shows no_match + duplicates breakdown in output.
  - Warns clearly when pointed at a pre-V3.4 unmatched file that
    lacks the Reason column.

USAGE:
  1. Update PARSED_AD_FILE and UNMATCHED_FILE below to point at the
     files from the run you want to summarize.
  2. Optionally update RUN_DATE to label the output.
  3. Run the script. Stats print to console.

Author: John Segars / Claude
Date: May 2026
"""

import pandas as pd
import os
from datetime import datetime

# ============================================================
# CONFIGURATION — update these for each run you want to review
# ============================================================

# Output of AD_Parsing_V3.6 (or later)
PARSED_AD_FILE = r"C:\Users\jdsegars\Documents\ArcGIS\Scripts\ActiveDirectoryParsing\FacStaffWithAddress_05202026_parsed.xlsx"

# Output of Campus_Floor_Plans_INFO_update_PROD (timestamped)
UNMATCHED_FILE = r"C:\Users\jdsegars\Documents\ArcGIS\Scripts\ActiveDirectoryParsing\Unmatched_AD_Rooms_20260520_095758.xlsx"

# Label for the run — used in the summary header
# Set to None to auto-detect from the parsed filename
RUN_DATE = None

# ============================================================
# CONFIGURATION — column names
# These match the output of the current scripts. Update here
# if column names change in a future script version.
# ============================================================

# Parsed AD file columns
COL_BUILDING  = 'Building'
COL_ROOM      = 'Room'
COL_CITY      = 'City'
COL_SUSPECT   = 'Suspect'
COL_SOURCE    = 'Source'

# Unmatched file columns
# The updater writes: GIS_Bldg, Room, Surname, Dept_Code, Email, Reason
# 'Reason' values include: 'parse_error', 'duplicate', 'no_match'
COL_REASON    = 'Reason'

# Output path for the HTML summary page.
# Set to None to skip HTML generation.
# Copy the output file to GitHub for Leaflet/Hub presentation.
HTML_OUTPUT_FILE = r"C:\Users\jdsegars\Documents\ArcGIS\Scripts\ActiveDirectoryParsing\pipeline_summary.html"

# Path to the pipeline history JSON file.
# The script appends one record per run. Copy this to GitHub alongside
# pipeline_summary.html and pipeline_trend.html after each run.
# Set to None to skip history tracking.
HISTORY_JSON_FILE = r"C:\Users\jdsegars\Documents\ArcGIS\Scripts\ActiveDirectoryParsing\pipeline_history.json"

# Output path for the trend HTML page.
# Set to None to skip trend page generation.
TREND_HTML_FILE = r"C:\Users\jdsegars\Documents\ArcGIS\Scripts\ActiveDirectoryParsing\pipeline_trend.html"

# ============================================================
# SCRIPT — no changes needed below this line
# ============================================================

def has_value(v):
    """Returns True if v is a non-empty, non-null string."""
    if v is None:
        return False
    if pd.isna(v):
        return False
    return str(v).strip() not in ('', 'nan')


def load_parsed_ad(filepath):
    """Load and validate the parsed AD Excel file."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Parsed AD file not found:\n  {filepath}")
    print(f"  Reading parsed AD file: {os.path.basename(filepath)}")
    df = pd.read_excel(filepath, dtype=str)
    for col in [COL_BUILDING, COL_ROOM, COL_CITY]:
        if col not in df.columns:
            raise ValueError(f"Expected column '{col}' not found in parsed AD file.")
    return df


def load_unmatched(filepath):
    """Load and validate the unmatched AD rooms Excel file."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Unmatched file not found:\n  {filepath}")
    print(f"  Reading unmatched file:  {os.path.basename(filepath)}")
    df = pd.read_excel(filepath, dtype=str)
    return df


def calc_stats(df_parsed, df_unmatched):
    """
    Calculate all six briefing statistics plus gap breakdown.

    Returns a dict with all values.
    """
    stats = {}

    # --- Primary source rows only (exclude secondary postaladdress rows) ---
    # Secondary rows would double-count people with two offices
    if COL_SOURCE in df_parsed.columns:
        df_primary = df_parsed[df_parsed[COL_SOURCE] == 'physicaldeliveryofficename'].copy()
    else:
        df_primary = df_parsed.copy()

    # 1. Total AD Accounts — all primary rows
    stats['total_ad'] = len(df_primary)

    # 2. Suspect records excluded
    if COL_SUSPECT in df_primary.columns:
        stats['suspect'] = (df_primary[COL_SUSPECT].fillna('') == 'Y').sum()
    else:
        stats['suspect'] = 0

    # 3. Online / blank / No Office
    online_mask = (
        (df_primary[COL_CITY].fillna('').str.strip().str.lower() == 'online') |
        (df_primary[COL_BUILDING].fillna('').str.strip().str.lower() == 'no office') |
        (
            (~df_primary[COL_BUILDING].apply(has_value)) &
            (~df_primary[COL_ROOM].apply(has_value)) &
            (~df_primary[COL_CITY].apply(has_value))
        )
    )
    stats['online_blank'] = online_mask.sum()

    # 4. Missing Building / Room / City (but not blank/online/suspect)
    complete_mask = (
        df_primary[COL_BUILDING].apply(has_value) &
        df_primary[COL_ROOM].apply(has_value) &
        df_primary[COL_CITY].apply(has_value)
    )
    suspect_mask = df_primary[COL_SUSPECT].fillna('') == 'Y' \
        if COL_SUSPECT in df_primary.columns \
        else pd.Series([False] * len(df_primary))

    stats['missing_location'] = (
        ~complete_mask & ~online_mask & ~suspect_mask
    ).sum()

    # 5. Mappable — complete location, not suspect, not online/blank
    stats['mappable'] = (complete_mask & ~suspect_mask & ~online_mask).sum()

    # 6. Gap breakdown from unmatched file
    stats['gap_duplicates']   = 0
    stats['gap_no_polygon']   = 0
    stats['gap_other']        = 0
    stats['gap_total']        = len(df_unmatched) if df_unmatched is not None else 0

    if df_unmatched is not None and COL_REASON in df_unmatched.columns:
        reason_counts = df_unmatched[COL_REASON].fillna('').str.strip().str.lower().value_counts()
        stats['gap_duplicates'] = int(reason_counts.get('duplicate', 0))
        stats['gap_no_polygon'] = int(reason_counts.get('no_match', 0))
        stats['gap_other']      = stats['gap_total'] - \
                                  stats['gap_duplicates'] - \
                                  stats['gap_no_polygon']
        # With Reason column present, GIS Populated = Mappable - no_match - duplicates
        # (duplicates are skipped, not populated)
        stats['gis_populated']  = stats['mappable'] - stats['gap_no_polygon'] - stats['gap_duplicates']
    elif df_unmatched is not None:
        # Reason column not present (pre-V3.4 unmatched file) — report total only
        # GIS Populated cannot be accurately derived without the Reason breakdown
        stats['gap_no_polygon'] = stats['gap_total']
        stats['gis_populated']  = stats['mappable'] - stats['gap_total']
        stats['reason_col_missing'] = True
    else:
        stats['gis_populated'] = 0

    if stats['gis_populated'] < 0:
        stats['gis_populated'] = 0

    if stats['mappable'] > 0:
        stats['placement_rate'] = (stats['gis_populated'] / stats['mappable']) * 100
    else:
        stats['placement_rate'] = 0.0

    # 8. Always 5
    stats['campuses_live'] = 5

    return stats


def print_summary(stats, run_label):
    """Print the summary in briefing format."""
    w = 70
    print()
    print("=" * w)
    print(f"  PIPELINE SUMMARY STATS — {run_label}")
    print("=" * w)

    print(f"\n  {'BRIEFING BOX STATISTICS':}")
    print(f"  {'-' * 50}")
    print(f"  Total AD Accounts          : {stats['total_ad']:>6,}")
    print(f"  Mappable Records           : {stats['mappable']:>6,}   (complete Bldg + Room + City)")
    print(f"  GIS Polygons Populated     : {stats['gis_populated']:>6,}")
    print(f"  Placement Rate             : {stats['placement_rate']:>6.1f}%")
    print(f"  Campuses Live              : {stats['campuses_live']:>6}")
    gap_display = stats['gap_no_polygon'] + stats['gap_duplicates']
    print(f"  Gap Records                : {gap_display:>6,}   "
          f"({stats['gap_no_polygon']} no_match + {stats['gap_duplicates']} duplicates)")

    if stats.get('reason_col_missing'):
        print(f"\n  NOTE: Unmatched file has no Reason column (pre-V3.4 output).")
        print(f"        Gap breakdown and GIS Populated count may be inaccurate.")
        print(f"        Re-run with updater V3.4+ to get full breakdown.")

    print(f"\n  {'POPULATION BREAKDOWN':}")
    print(f"  {'-' * 50}")
    print(f"  Total AD accounts          : {stats['total_ad']:>6,}")
    print(f"  Suspect (no fixed office)  : {stats['suspect']:>6,}")
    print(f"  Online / blank / No Office : {stats['online_blank']:>6,}")
    print(f"  Missing Bldg/Room/City     : {stats['missing_location']:>6,}")
    print(f"  Mappable population        : {stats['mappable']:>6,}")

    print(f"\n  {'GAP BREAKDOWN':}")
    print(f"  {'-' * 50}")
    print(f"  Duplicate polygons skipped : {stats['gap_duplicates']:>6,}")
    print(f"  No matching GIS polygon    : {stats['gap_no_polygon']:>6,}")
    print(f"  Other / crosswalk misses   : {stats['gap_other']:>6,}")
    print(f"  Total gap                  : {stats['gap_total']:>6,}")

    print()
    print("=" * w)
    print(f"  Source files:")
    print(f"    Parsed AD : {os.path.basename(PARSED_AD_FILE)}")
    print(f"    Unmatched : {os.path.basename(UNMATCHED_FILE)}")
    print("=" * w)
    print()


def get_run_label():
    """
    Returns RUN_DATE if set, otherwise attempts to parse a date from
    the parsed AD filename (e.g. FacStaffWithAddress_05202026_parsed.xlsx
    → May 20, 2026).
    """
    if RUN_DATE:
        return RUN_DATE

    basename = os.path.basename(PARSED_AD_FILE)
    # Look for an 8-digit date in MMDDYYYY format embedded in the filename
    import re
    match = re.search(r'(\d{8})', basename)
    if match:
        date_str = match.group(1)
        try:
            dt = datetime.strptime(date_str, '%m%d%Y')
            return dt.strftime('%B %d, %Y')
        except ValueError:
            pass

    return os.path.basename(PARSED_AD_FILE)


def generate_html(stats, run_label, output_path):
    """
    Write a UNG-branded HTML summary page to output_path.
    Designed for GitHub hosting and Leaflet/Hub presentation.
    """
    gap_no_match   = stats['gap_no_polygon']
    gap_duplicates = stats['gap_duplicates']
    gap_total      = gap_no_match + gap_duplicates
    gap_other      = stats.get('gap_other', 0)
    placement      = stats['placement_rate']
    generated_ts   = datetime.now().strftime('%B %d, %Y at %I:%M %p')

    # Placement rate color — green >= 80, amber >= 65, red below
    if placement >= 80:
        rate_color = '#2d7a3a'
    elif placement >= 65:
        rate_color = '#b07d00'
    else:
        rate_color = '#a63228'

    gap_other_row = ''
    if gap_other > 0:
        gap_other_row = f"""
        <tr>
          <td>Other / crosswalk misses</td>
          <td>{gap_other:,}</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>UNG Facilities GIS — Pipeline Summary</title>
  <link href="https://fonts.googleapis.com/css2?family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&family=Source+Sans+3:wght@300;400;600&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    :root {{
      --navy:       #1a2a4a;
      --navy-mid:   #243558;
      --navy-light: #2e4270;
      --gold:       #c9a84c;
      --gold-light: #e8d49a;
      --gold-pale:  #f7f1e0;
      --white:      #ffffff;
      --off-white:  #f8f7f4;
      --text:       #1e2532;
      --muted:      #5a6478;
      --rule:       #ddd8cc;
      --green:      #2d7a3a;
      --amber:      #b07d00;
      --red:        #a63228;
      --red-pale:   #fdf1f0;
      --blue-pale:  #f0f4fa;
    }}

    body {{
      font-family: 'Source Sans 3', sans-serif;
      font-weight: 300;
      background: var(--off-white);
      color: var(--text);
      min-height: 100vh;
    }}

    /* ── HEADER ── */
    header {{
      background: var(--navy);
      padding: 0;
      border-bottom: 3px solid var(--gold);
    }}
    .header-inner {{
      max-width: 900px;
      margin: 0 auto;
      padding: 28px 32px 22px;
      display: flex;
      align-items: flex-end;
      justify-content: space-between;
      gap: 20px;
    }}
    .header-brand {{
      display: flex;
      flex-direction: column;
      gap: 4px;
    }}
    .header-eyebrow {{
      font-family: 'Source Sans 3', sans-serif;
      font-weight: 600;
      font-size: 10px;
      letter-spacing: 0.18em;
      text-transform: uppercase;
      color: var(--gold);
    }}
    .header-title {{
      font-family: 'Libre Baskerville', serif;
      font-size: 22px;
      font-weight: 700;
      color: var(--white);
      line-height: 1.2;
    }}
    .header-sub {{
      font-size: 13px;
      font-weight: 300;
      color: var(--gold-light);
      margin-top: 2px;
    }}
    .header-date {{
      text-align: right;
      flex-shrink: 0;
    }}
    .date-label {{
      font-size: 10px;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: var(--gold);
      font-weight: 600;
    }}
    .date-value {{
      font-family: 'Libre Baskerville', serif;
      font-size: 17px;
      color: var(--white);
      margin-top: 3px;
      font-style: italic;
    }}

    /* ── MAIN ── */
    main {{
      max-width: 900px;
      margin: 0 auto;
      padding: 36px 32px 60px;
    }}

    /* ── SECTION HEADER ── */
    .section-label {{
      font-size: 10px;
      font-weight: 600;
      letter-spacing: 0.16em;
      text-transform: uppercase;
      color: var(--gold);
      margin-bottom: 14px;
      padding-bottom: 8px;
      border-bottom: 1px solid var(--rule);
    }}

    /* ── SIX STAT BOXES ── */
    .stat-grid {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 14px;
      margin-bottom: 40px;
    }}
    .stat-box {{
      background: var(--white);
      border: 1px solid var(--rule);
      border-top: 3px solid var(--navy-light);
      padding: 20px 18px 18px;
      border-radius: 2px;
    }}
    .stat-box.gold-top   {{ border-top-color: var(--gold); }}
    .stat-box.green-top  {{ border-top-color: var(--green); }}
    .stat-box.red-top    {{ border-top-color: var(--red); }}
    .stat-number {{
      font-family: 'Libre Baskerville', serif;
      font-size: 34px;
      font-weight: 700;
      line-height: 1;
      color: var(--navy);
    }}
    .stat-number.rate    {{ color: {rate_color}; }}
    .stat-number.gap     {{ color: var(--red); }}
    .stat-label {{
      font-size: 11px;
      font-weight: 600;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      color: var(--muted);
      margin-top: 6px;
    }}
    .stat-sub {{
      font-size: 11px;
      color: var(--muted);
      margin-top: 3px;
      line-height: 1.4;
    }}

    /* ── TABLES ── */
    .table-section {{ margin-bottom: 38px; }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 13.5px;
      background: var(--white);
      border: 1px solid var(--rule);
    }}
    thead tr {{
      background: var(--navy);
      color: var(--white);
    }}
    thead th {{
      padding: 10px 16px;
      text-align: left;
      font-weight: 600;
      font-size: 11px;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }}
    thead th:last-child {{ text-align: right; }}
    tbody tr {{ border-bottom: 1px solid var(--rule); }}
    tbody tr:last-child {{ border-bottom: none; }}
    tbody tr.subtotal {{
      background: var(--blue-pale);
      font-weight: 600;
    }}
    tbody tr.total {{
      background: var(--navy);
      color: var(--white);
      font-weight: 600;
    }}
    tbody tr.gap-row {{ background: var(--red-pale); }}
    tbody td {{
      padding: 10px 16px;
      vertical-align: top;
      line-height: 1.4;
    }}
    tbody td:last-child {{
      text-align: right;
      font-variant-numeric: tabular-nums;
      white-space: nowrap;
    }}
    .minus {{ color: var(--muted); }}

    /* ── PIPELINE STEPS ── */
    .steps-grid {{
      display: grid;
      grid-template-columns: auto 1fr;
      gap: 0;
      background: var(--white);
      border: 1px solid var(--rule);
      overflow: hidden;
    }}
    .step-num {{
      background: var(--navy);
      color: var(--gold);
      font-family: 'Libre Baskerville', serif;
      font-size: 13px;
      font-weight: 700;
      padding: 12px 16px;
      text-align: center;
      border-bottom: 1px solid var(--navy-light);
      min-width: 48px;
    }}
    .step-content {{
      padding: 11px 16px;
      border-bottom: 1px solid var(--rule);
      font-size: 13px;
      line-height: 1.45;
    }}
    .step-num:last-of-type,
    .step-content:last-of-type {{ border-bottom: none; }}
    .step-name {{
      font-weight: 600;
      color: var(--navy);
    }}
    .step-desc {{
      color: var(--muted);
      font-size: 12px;
      margin-top: 1px;
    }}

    /* ── FOOTER ── */
    footer {{
      background: var(--navy);
      border-top: 3px solid var(--gold);
      padding: 18px 32px;
      text-align: center;
    }}
    .footer-inner {{
      max-width: 900px;
      margin: 0 auto;
      font-size: 11px;
      color: var(--gold-light);
      line-height: 1.7;
    }}
    .footer-inner strong {{ color: var(--white); }}

    @media (max-width: 600px) {{
      .stat-grid {{ grid-template-columns: repeat(2, 1fr); }}
      .header-inner {{ flex-direction: column; align-items: flex-start; }}
      .header-date {{ text-align: left; }}
    }}
  </style>
</head>
<body>

<header>
  <div class="header-inner">
    <div class="header-brand">
      <div class="header-eyebrow">University of North Georgia · Facilities Planning &amp; GIS</div>
      <div class="header-title">AD → GIS Floor Plan Pipeline</div>
      <div class="header-sub">Weekly occupant data refresh across all five campuses</div>
    </div>
    <div class="header-date">
      <div class="date-label">Data as of</div>
      <div class="date-value">{run_label}</div>
    </div>
  </div>
</header>

<main>

  <!-- SIX STAT BOXES -->
  <div class="section-label">Pipeline Results</div>
  <div class="stat-grid">

    <div class="stat-box">
      <div class="stat-number">{stats['total_ad']:,}</div>
      <div class="stat-label">Total AD Accounts</div>
      <div class="stat-sub">Full UNG workforce</div>
    </div>

    <div class="stat-box">
      <div class="stat-number">{stats['mappable']:,}</div>
      <div class="stat-label">Mappable Records</div>
      <div class="stat-sub">Complete Bldg + Room + City in AD</div>
    </div>

    <div class="stat-box gold-top">
      <div class="stat-number">{stats['gis_populated']:,}</div>
      <div class="stat-label">GIS Polygons Populated</div>
      <div class="stat-sub">Rooms with confirmed occupant</div>
    </div>

    <div class="stat-box green-top">
      <div class="stat-number rate">{placement:.1f}%</div>
      <div class="stat-label">Placement Rate</div>
      <div class="stat-sub">Of mappable AD records</div>
    </div>

    <div class="stat-box">
      <div class="stat-number">5</div>
      <div class="stat-label">Campuses Live</div>
      <div class="stat-sub">BRC, CC, DC, GC, OC</div>
    </div>

    <div class="stat-box red-top">
      <div class="stat-number gap">{gap_total:,}</div>
      <div class="stat-label">Gap Records</div>
      <div class="stat-sub">Mappable but not placed — reasons below</div>
    </div>

  </div>

  <!-- POPULATION BREAKDOWN -->
  <div class="table-section">
    <div class="section-label">Understanding the Numbers</div>
    <table>
      <thead>
        <tr><th>Population Category</th><th>Count</th></tr>
      </thead>
      <tbody>
        <tr><td>Total AD accounts</td><td>{stats['total_ad']:,}</td></tr>
        <tr><td><span class="minus">−</span> Flagged Suspect — part-time, adjunct, no fixed office expected</td><td>− {stats['suspect']:,}</td></tr>
        <tr><td><span class="minus">−</span> Online / blank / No Office designation</td><td>− {stats['online_blank']:,}</td></tr>
        <tr><td><span class="minus">−</span> Missing building, room, or city data in AD</td><td>− {stats['missing_location']:,}</td></tr>
        <tr class="subtotal"><td>Mappable population (should have a room)</td><td>{stats['mappable']:,}</td></tr>
        <tr><td>GIS polygons successfully populated</td><td>{stats['gis_populated']:,}</td></tr>
        <tr><td>Placement rate against mappable population</td><td>{placement:.1f}%</td></tr>
        <tr class="gap-row"><td>Gap — mappable records not placed on a polygon</td><td>{gap_total:,}</td></tr>
      </tbody>
    </table>
  </div>

  <!-- GAP BREAKDOWN -->
  <div class="table-section">
    <div class="section-label">The {gap_total:,} Gap — Accounted For</div>
    <table>
      <thead>
        <tr><th>Gap Category</th><th>Count</th></tr>
      </thead>
      <tbody>
        <tr>
          <td>Duplicate GIS polygons — intentionally skipped to prevent ambiguous writes</td>
          <td>{gap_duplicates:,}</td>
        </tr>
        <tr>
          <td>AD room entries with no matching GIS polygon (new construction, unofficial designations, entry variants)</td>
          <td>{gap_no_match:,}</td>
        </tr>{gap_other_row}
        <tr class="total"><td>Total gap</td><td>{gap_total:,}</td></tr>
      </tbody>
    </table>
  </div>

  <!-- PIPELINE STEPS -->
  <div class="table-section">
    <div class="section-label">What Powers This System — Weekly Pipeline</div>
    <div class="steps-grid">
      <div class="step-num">1</div>
      <div class="step-content">
        <div class="step-name">AD Parsing</div>
        <div class="step-desc">{stats['total_ad']:,} records parsed; suspect records filtered; primary + secondary office locations extracted</div>
      </div>
      <div class="step-num">2</div>
      <div class="step-content">
        <div class="step-name">Email List Creation</div>
        <div class="step-desc">Distribution lists generated from parsed AD output for space inventory campaigns</div>
      </div>
      <div class="step-num">3</div>
      <div class="step-content">
        <div class="step-name">Building Crosswalk</div>
        <div class="step-desc">95 verified mappings translate AD free-text building names to GIS building codes</div>
      </div>
      <div class="step-num">4</div>
      <div class="step-content">
        <div class="step-name">Department Crosswalk</div>
        <div class="step-desc">108 department mappings with city disambiguation; 96 room range overrides applied</div>
      </div>
      <div class="step-num">5</div>
      <div class="step-content">
        <div class="step-name">GIS Field Clear</div>
        <div class="step-desc">All occupant fields blanked across 5 campus feature classes — integrity by design</div>
      </div>
      <div class="step-num">6</div>
      <div class="step-content">
        <div class="step-name">AD Updater</div>
        <div class="step-desc">{stats['gis_populated']:,} room polygons written; automatic backup created per campus before any write</div>
      </div>
      <div class="step-num">7</div>
      <div class="step-content">
        <div class="step-name">Campus Floor Plans Merge</div>
        <div class="step-desc">5 campus feature classes merged into enterprise geodatabase with duplicate GUID detection</div>
      </div>
      <div class="step-num">8</div>
      <div class="step-content">
        <div class="step-name">FICM CFP Prep</div>
        <div class="step-desc">Floor plan data staged for FICM-compliant export</div>
      </div>
      <div class="step-num">9</div>
      <div class="step-content">
        <div class="step-name">Floor Plan Exporter</div>
        <div class="step-desc">218 PDFs exported (0 errors); 3 space reports; 5 campus XLSX workbooks; 223 files pushed to SharePoint automatically</div>
      </div>
      <div class="step-num">10</div>
      <div class="step-content">
        <div class="step-name">Banner Action List</div>
        <div class="step-desc">GIS vs. Banner space inventory discrepancies flagged for reconciliation</div>
      </div>
    </div>
  </div>

</main>

<footer>
  <div class="footer-inner">
    <strong>UNG Facilities Planning &amp; GIS</strong> &nbsp;·&nbsp;
    Data as of {run_label} &nbsp;·&nbsp;
    Generated {generated_ts}<br>
    Source: AD → GIS Floor Plan Pipeline &nbsp;·&nbsp; Internal use
  </div>
</footer>

</body>
</html>"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"\n  HTML summary written to: {output_path}")


def update_history(stats, run_label, history_path):
    """
    Append the current run's stats to pipeline_history.json.
    Creates the file if it does not exist.
    Deduplicates by run_label so re-running the same day overwrites rather
    than appending a duplicate entry.
    """
    import json

    record = {
        'run_date':       datetime.now().strftime('%Y-%m-%d'),
        'run_label':      run_label,
        'total_ad':       int(stats['total_ad']),
        'mappable':       int(stats['mappable']),
        'suspect':        int(stats['suspect']),
        'online_blank':   int(stats['online_blank']),
        'missing_location': int(stats['missing_location']),
        'gis_populated':  int(stats['gis_populated']),
        'placement_rate': round(float(stats['placement_rate']), 2),
        'gap_no_match':   int(stats['gap_no_polygon']),
        'gap_duplicates': int(stats['gap_duplicates']),
    }

    history = []
    if os.path.exists(history_path):
        try:
            with open(history_path, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except (json.JSONDecodeError, IOError):
            print(f"  WARNING: Could not read existing history file — starting fresh.")

    # Remove any existing entry for the same run_label (idempotent)
    history = [h for h in history if h.get('run_label') != run_label]
    history.append(record)

    # Sort chronologically
    history.sort(key=lambda h: h['run_date'])

    with open(history_path, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2)

    print(f"  History updated ({len(history)} runs): {history_path}")
    return history


def generate_trend_html(history, output_path):
    """
    Write the UNG-branded pipeline trend HTML page to output_path.
    Embeds the full history as a JavaScript array so the page is
    self-contained — no server required for GitHub Pages hosting.
    """
    import json

    history_json = json.dumps(history, indent=2)

    # Read the template and inject the data
    template_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'pipeline_trend_template.html'
    )

    if not os.path.exists(template_path):
        print(f"  WARNING: Trend template not found at {template_path}")
        print(f"           Copy pipeline_trend_template.html to the same folder as this script.")
        return

    with open(template_path, 'r', encoding='utf-8') as f:
        html = f.read()

    html = html.replace('PIPELINE_HISTORY_PLACEHOLDER', history_json)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"  Trend page written to: {output_path}")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("\nPipeline Summary Stats V1.0")
    print("Loading files...")

    try:
        df_parsed   = load_parsed_ad(PARSED_AD_FILE)
        df_unmatched = load_unmatched(UNMATCHED_FILE) \
            if UNMATCHED_FILE and os.path.exists(UNMATCHED_FILE) \
            else None

        if df_unmatched is None:
            print("  NOTE: Unmatched file not found — gap breakdown will be omitted.")

        stats     = calc_stats(df_parsed, df_unmatched)
        run_label = get_run_label()

        print_summary(stats, run_label)

        if HTML_OUTPUT_FILE:
            generate_html(stats, run_label, HTML_OUTPUT_FILE)
            print(f"  Copy to GitHub for Leaflet/Hub presentation.")

        if HISTORY_JSON_FILE:
            history = update_history(stats, run_label, HISTORY_JSON_FILE)
            if TREND_HTML_FILE and len(history) >= 1:
                generate_trend_html(history, TREND_HTML_FILE)
                print(f"  Copy pipeline_trend.html and pipeline_history.json to GitHub.")

    except FileNotFoundError as e:
        print(f"\nERROR: {e}")
    except ValueError as e:
        print(f"\nERROR: {e}")
    except Exception as e:
        import traceback
        print(f"\nUnexpected error: {e}")
        traceback.print_exc()
# check
