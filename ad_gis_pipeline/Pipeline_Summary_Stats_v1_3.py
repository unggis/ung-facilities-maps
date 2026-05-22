"""
Pipeline Summary Stats V1.3
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

CHANGES IN V1.3:
  - Reads gap_gis_duplicates from the Meta sheet in the unmatched
    Excel file (written by updater V3.6+). This is the actual count
    of duplicate building+room polygon pairs in GIS — separate from
    the AD records affected by those duplicates. The number is now
    driven by the data, not hardcoded. Older single-sheet unmatched
    files (pre-V3.6) are still supported; gap_gis_duplicates defaults
    to 0 if the Meta sheet is absent.
  - Fixed DeprecationWarning — now uses github.Auth.Token() correctly.
  - Fixed printed dashboard URL to show folder path not filename.
  - Local pipeline_history.json is now written after each GitHub push
    so the local copy stays in sync with GitHub.

CHANGES IN V1.2:
  - Adds optional GitHub push via PyGithub.
  - Set GITHUB_TOKEN = "" to skip GitHub push (print only).
  - Requires PyGithub: pip install PyGithub

CHANGES IN V1.1:
  - Reads Reason column from unmatched file (added in updater V3.4).
  - Gap Records now shows no_match + duplicates breakdown in output.
  - Warns clearly when pointed at a pre-V3.4 unmatched file that
    lacks the Reason column.

USAGE:
  1. Update PARSED_AD_FILE and UNMATCHED_FILE below to point at the
     files from the run you want to summarize.
  2. Optionally update RUN_DATE to label the output.
  3. Set GITHUB_TOKEN to your personal access token to enable push.
  4. Run the script. Stats print to console. If token is set,
     pipeline_history.json and index.html are pushed to GitHub,
     and the local pipeline_history.json is updated to match.

Author: John Segars / Claude
Date: May 2026
"""

import pandas as pd
import os
import json
import re
from datetime import datetime

# ============================================================
# CONFIGURATION — update these for each run
# ============================================================

# Output of AD_Parsing_V3.6 (or later)
PARSED_AD_FILE = r"C:\Users\jdsegars\Documents\ArcGIS\Scripts\ActiveDirectoryParsing\FacStaffWithAddress_05222026AM_parsed.xlsx"

# Output of Campus_Floor_Plans_INFO_update_PROD (timestamped)
UNMATCHED_FILE = r"C:\Users\jdsegars\Documents\ArcGIS\Scripts\ActiveDirectoryParsing\Unmatched_AD_Rooms_20260522_091759.xlsx"

# Label for the run — set to None to auto-detect from the parsed filename
RUN_DATE = None

# ============================================================
# LOCAL JSON PATH
# Path to the local copy of pipeline_history.json.
# Updated automatically after each GitHub push to stay in sync.
# ============================================================

LOCAL_JSON_PATH = r"C:\Users\jdsegars\Documents\ArcGIS\Scripts\Pipeline\pipeline_history.json"

# ============================================================
# GITHUB CONFIGURATION — set token to enable automatic push
# Leave GITHUB_TOKEN as "" to skip GitHub push (print only)
# ============================================================

# Paste your personal access token here (public_repo scope)
GITHUB_TOKEN = ""

# Repo and paths — no changes needed unless structure changes
GITHUB_REPO      = "unggis/ung-facilities-maps"
GITHUB_JSON_PATH = "ad_gis_pipeline/pipeline_history.json"
GITHUB_HTML_PATH = "ad_gis_pipeline/index.html"
GITHUB_TMPL_PATH = "ad_gis_pipeline/pipeline_trend_template.html"

# ============================================================
# CONFIGURATION — column names
# ============================================================

COL_BUILDING = 'Building'
COL_ROOM     = 'Room'
COL_CITY     = 'City'
COL_SUSPECT  = 'Suspect'
COL_SOURCE   = 'Source'
COL_REASON   = 'Reason'

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
    """
    Load the unmatched AD rooms Excel file.
    V3.6+ files have two sheets:
      'Unmatched' — AD records that could not be placed
      'Meta'      — key/value pairs including gap_gis_duplicates
    Older single-sheet files are still supported.
    Returns (df_unmatched, meta_dict).
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Unmatched file not found:\n  {filepath}")
    print(f"  Reading unmatched file:  {os.path.basename(filepath)}")

    xl   = pd.ExcelFile(filepath)
    meta = {}

    if 'Unmatched' in xl.sheet_names:
        df = pd.read_excel(xl, sheet_name='Unmatched', dtype=str)
        if 'Meta' in xl.sheet_names:
            df_meta = pd.read_excel(xl, sheet_name='Meta', dtype=str)
            for _, row in df_meta.iterrows():
                meta[row['key']] = row['value']
            print(f"  Meta sheet found — gap_gis_duplicates: "
                  f"{meta.get('gap_gis_duplicates', 'not set')}")
        else:
            print("  No Meta sheet — pre-V3.6 file, gap_gis_duplicates not available.")
    else:
        # Older single-sheet format
        df = pd.read_excel(xl, dtype=str)
        print("  Single-sheet format — pre-V3.6 file.")

    return df, meta


def calc_stats(df_parsed, df_unmatched, meta):
    """Calculate all six briefing statistics plus gap breakdown."""
    stats = {}

    if COL_SOURCE in df_parsed.columns:
        df_primary = df_parsed[df_parsed[COL_SOURCE] == 'physicaldeliveryofficename'].copy()
    else:
        df_primary = df_parsed.copy()

    stats['total_ad'] = len(df_primary)

    if COL_SUSPECT in df_primary.columns:
        stats['suspect'] = (df_primary[COL_SUSPECT].fillna('') == 'Y').sum()
    else:
        stats['suspect'] = 0

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

    stats['mappable'] = (complete_mask & ~suspect_mask & ~online_mask).sum()

    # GIS duplicate polygon count — from Meta sheet if available
    stats['gap_gis_duplicates'] = int(meta.get('gap_gis_duplicates', 0))

    stats['gap_duplicates'] = 0
    stats['gap_no_polygon'] = 0
    stats['gap_other']      = 0
    stats['gap_total']      = len(df_unmatched) if df_unmatched is not None else 0

    if df_unmatched is not None and COL_REASON in df_unmatched.columns:
        reason_counts = df_unmatched[COL_REASON].fillna('').str.strip().str.lower().value_counts()
        stats['gap_duplicates'] = int(reason_counts.get('duplicate', 0))
        stats['gap_no_polygon'] = int(reason_counts.get('no_match', 0))
        stats['gap_other']      = stats['gap_total'] - stats['gap_duplicates'] - stats['gap_no_polygon']
        stats['gis_populated']  = stats['mappable'] - stats['gap_no_polygon'] - stats['gap_duplicates']
    elif df_unmatched is not None:
        stats['gap_no_polygon']     = stats['gap_total']
        stats['gis_populated']      = stats['mappable'] - stats['gap_total']
        stats['reason_col_missing'] = True
    else:
        stats['gis_populated'] = 0

    if stats['gis_populated'] < 0:
        stats['gis_populated'] = 0

    stats['placement_rate'] = (
        (stats['gis_populated'] / stats['mappable']) * 100
        if stats['mappable'] > 0 else 0.0
    )
    stats['campuses_live'] = 5

    return stats


def get_run_label():
    """Returns RUN_DATE if set, otherwise parses date from parsed AD filename."""
    if RUN_DATE:
        return RUN_DATE
    basename = os.path.basename(PARSED_AD_FILE)
    match = re.search(r'(\d{8})', basename)
    if match:
        try:
            dt = datetime.strptime(match.group(1), '%m%d%Y')
            return dt.strftime('%B %d, %Y')
        except ValueError:
            pass
    return basename


def get_run_date():
    """Returns ISO date string for the run — today if not auto-detected."""
    basename = os.path.basename(PARSED_AD_FILE)
    match = re.search(r'(\d{8})', basename)
    if match:
        try:
            dt = datetime.strptime(match.group(1), '%m%d%Y')
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            pass
    return datetime.today().strftime('%Y-%m-%d')


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
          f"({stats['gap_no_polygon']} no_match + {stats['gap_duplicates']} AD duplicates)")

    if stats.get('reason_col_missing'):
        print(f"\n  NOTE: Unmatched file has no Reason column (pre-V3.4 output).")
        print(f"        Gap breakdown and GIS Populated count may be inaccurate.")

    print(f"\n  {'POPULATION BREAKDOWN':}")
    print(f"  {'-' * 50}")
    print(f"  Total AD accounts          : {stats['total_ad']:>6,}")
    print(f"  Suspect (no fixed office)  : {stats['suspect']:>6,}")
    print(f"  Online / blank / No Office : {stats['online_blank']:>6,}")
    print(f"  Missing Bldg/Room/City     : {stats['missing_location']:>6,}")
    print(f"  Mappable population        : {stats['mappable']:>6,}")

    print(f"\n  {'GAP BREAKDOWN':}")
    print(f"  {'-' * 50}")
    print(f"  AD records hit duplicates  : {stats['gap_duplicates']:>6,}   (varies by run)")
    print(f"  GIS duplicate polygons     : {stats['gap_gis_duplicates']:>6,}   (from Meta sheet)")
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


def push_to_github(stats, run_label, run_date_iso):
    """
    Appends the new run to pipeline_history.json and regenerates
    index.html, then pushes both to GitHub. Also writes the updated
    JSON to the local file to keep it in sync.
    """
    try:
        from github import Auth, Github
    except ImportError:
        print("\n  GitHub push SKIPPED — PyGithub not installed.")
        print("  Run: pip install PyGithub")
        return

    print("\n  Connecting to GitHub...")
    auth = Auth.Token(GITHUB_TOKEN)
    g    = Github(auth=auth)
    repo = g.get_repo(GITHUB_REPO)

    # ── 1. Update pipeline_history.json ──────────────────────────────
    print(f"  Fetching {GITHUB_JSON_PATH}...")
    json_file = repo.get_contents(GITHUB_JSON_PATH)
    history   = json.loads(json_file.decoded_content.decode('utf-8'))

    existing_dates = [r['run_date'] for r in history]
    new_record = {
        "run_date"           : run_date_iso,
        "run_label"          : run_label,
        "total_ad"           : int(stats['total_ad']),
        "mappable"           : int(stats['mappable']),
        "suspect"            : int(stats['suspect']),
        "online_blank"       : int(stats['online_blank']),
        "missing_location"   : int(stats['missing_location']),
        "gis_populated"      : int(stats['gis_populated']),
        "placement_rate"     : round(float(stats['placement_rate']), 1),
        "gap_no_match"       : int(stats['gap_no_polygon']),
        "gap_duplicates"     : int(stats['gap_duplicates']),
        "gap_gis_duplicates" : int(stats['gap_gis_duplicates'])
    }

    if run_date_iso in existing_dates:
        idx = existing_dates.index(run_date_iso)
        history[idx] = new_record
        action = "Updated"
    else:
        history.append(new_record)
        action = "Appended"

    updated_json = json.dumps(history, indent=2)
    print(f"  {action} run {run_date_iso} in history ({len(history)} total runs).")

    # ── 2. Regenerate index.html from template ────────────────────────
    print(f"  Fetching {GITHUB_TMPL_PATH}...")
    tmpl_file    = repo.get_contents(GITHUB_TMPL_PATH)
    template     = tmpl_file.decoded_content.decode('utf-8')
    updated_html = template.replace(
        'PIPELINE_HISTORY_PLACEHOLDER',
        json.dumps(history, indent=2)
    )

    if 'PIPELINE_HISTORY_PLACEHOLDER' in updated_html:
        print("\n  ERROR: Placeholder not found in template — HTML not updated.")
        print("         Check that pipeline_trend_template.html contains")
        print("         the text: PIPELINE_HISTORY_PLACEHOLDER")
        return

    # ── 3. Push both files to GitHub ──────────────────────────────────
    commit_msg = f"Pipeline run {run_date_iso} — {stats['placement_rate']:.1f}% placement rate"

    print(f"  Pushing {GITHUB_JSON_PATH}...")
    repo.update_file(
        json_file.path,
        commit_msg,
        updated_json,
        json_file.sha
    )

    print(f"  Pushing {GITHUB_HTML_PATH}...")
    html_file = repo.get_contents(GITHUB_HTML_PATH)
    repo.update_file(
        html_file.path,
        commit_msg,
        updated_html,
        html_file.sha
    )

    # ── 4. Write local JSON copy ──────────────────────────────────────
    try:
        local_dir = os.path.dirname(LOCAL_JSON_PATH)
        if local_dir and not os.path.exists(local_dir):
            os.makedirs(local_dir)
        with open(LOCAL_JSON_PATH, 'w', encoding='utf-8') as f:
            f.write(updated_json)
        print(f"  Local JSON updated: {LOCAL_JSON_PATH}")
    except Exception as e:
        print(f"  WARNING: Could not write local JSON — {e}")

    print()
    print("  ✓ GitHub push complete.")
    print(f"  Commit: {commit_msg}")
    print(f"  Dashboard live at:")
    print(f"  https://unggis.github.io/ung-facilities-maps/ad_gis_pipeline/")
    print()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("\nPipeline Summary Stats V1.3")
    print("Loading files...")

    try:
        df_parsed = load_parsed_ad(PARSED_AD_FILE)

        df_unmatched = None
        meta         = {}
        if UNMATCHED_FILE and os.path.exists(UNMATCHED_FILE):
            df_unmatched, meta = load_unmatched(UNMATCHED_FILE)
        else:
            print("  NOTE: Unmatched file not found — gap breakdown will be omitted.")

        stats        = calc_stats(df_parsed, df_unmatched, meta)
        run_label    = get_run_label()
        run_date_iso = get_run_date()

        print_summary(stats, run_label)

        if GITHUB_TOKEN:
            push_to_github(stats, run_label, run_date_iso)
        else:
            print("  GitHub push skipped — GITHUB_TOKEN not set.")
            print("  Set GITHUB_TOKEN in the configuration section to enable.")

    except FileNotFoundError as e:
        print(f"\nERROR: {e}")
    except ValueError as e:
        print(f"\nERROR: {e}")
    except Exception as e:
        import traceback
        print(f"\nUnexpected error: {e}")
        traceback.print_exc()
