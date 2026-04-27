import pandas as pd
import geopandas as gpd
import re

# ==========================================
# CONFIGURATION
# ==========================================
PARTNERS_FILE = 'BPS Partner Programs.xlsx'
SCHOOLS_FILE  = 'BPS_Schools.gpkg'

# Organizations confirmed as non-OST based on program type review
NOT_OST_ORGS = [
    "Catie's Closet, Inc",
    'LiveSchool',
    'Arbour Counseling Services, Allston',
    'The Home for Little Wanderers',
    'Boston University Wheelock College of Education and Human Development',
    'Youth Guidance',
    'Spoonfuls, Inc.',
    'Special Olympics Massachusetts',
    'Mass Insight Education and Research Institute, Inc.',
    'PartnerBPS Test Organization',
]

# Organizations added to inferred OST based on known program type
# These have NaN time but are confirmed OST providers
ADDITIONAL_INFERRED_OST_ORGS = [
    'YMCA of Greater Boston',
    'Little Voices After School @ The Channing',
    'Girls on the Run Greater Boston',
    "St. Stephen's Youth Programs",
    'Jamaica Plain Community Centers',
    '4Star Dance Studio',
]

# Time values that are explicitly not OST
NOT_OST_TIMES = [
    'School Day',
    'School Day (Class Time)',
    'School Day (Non-Class Time)',
    'School Day (Class Time), School Day (Non-Class Time)',
    'Summer',
    'Weekend',
    'Summer, Weekend',
    'School Day, Summer',  # KeySteps fix
]

# ==========================================
# GRADE BAND DEFINITIONS
# Program-level grades from Grades Served: field
# e.g., "'K2','1','2','3'"
# ==========================================
PREK_GRADES   = {'K0', 'K1', 'K2'}
ELEM_GRADES   = {'K', '1', '2', '3', '4', '5'}
MIDDLE_GRADES = {'6', '7', '8'}

def parse_program_grades(grade_str):
    """
    Parse BPS partner grade strings e.g. "'K2','1','2','3'"
    Returns set of grade values.
    """
    if pd.isna(grade_str) or str(grade_str).strip() == '':
        return set()
    grades = re.findall(r"'([^']+)'", str(grade_str))
    if not grades:
        grades = [g.strip() for g in str(grade_str).split(',')]
    return set(grades)

def school_applicable_bands(grades_field):
    """
    Parse shapefile GRADES field e.g. "PK,K,01,02,03,04,05,06,07,08"
    Returns which bands are applicable for this school.
    Pre-K:      school serves PK
    Elementary: school serves K or 01-05
    Middle:     school serves 06-08
    """
    if pd.isna(grades_field):
        return {'prek': False, 'elem': False, 'middle': False}
    parts = set(g.strip() for g in str(grades_field).split(','))
    return {
        'prek':   'PK' in parts,
        'elem':   bool(parts & {'K', '01', '02', '03', '04', '05'}),
        'middle': bool(parts & {'06', '07', '08'}),
    }

# ==========================================
# LOAD DATA
# ==========================================
print("Loading partner programs...")
partners = pd.read_excel(PARTNERS_FILE)
before = len(partners)

# Drop test records immediately
partners = partners[
    partners['Organization Name:'] != 'PartnerBPS Test Organization'
].copy()
print(f"  Loaded: {len(partners)} records "
      f"(dropped {before - len(partners)} test records)")

print("\nLoading schools...")
schools = gpd.read_file(SCHOOLS_FILE)
print(f"  Loaded: {len(schools)} schools")

# ==========================================
# OST CATEGORIZATION
# ==========================================

# Identify orgs appearing in confirmed OST time records
# These are used to infer OST for their NaN-time sibling records
ost_time_mask = partners['Time'].str.contains(
    'Afterschool|Before School', na=False, case=False
)
confirmed_ost_orgs = set(partners[ost_time_mask]['Organization Name:'].dropna())

# Combine with manually confirmed additions
all_inferred_ost_orgs = confirmed_ost_orgs | set(ADDITIONAL_INFERRED_OST_ORGS)

def categorize_ost(row):
    time = str(row['Time']).strip() if pd.notna(row['Time']) else ''
    org  = str(row['Organization Name:']).strip() \
           if pd.notna(row['Organization Name:']) else ''

    # Confirmed OST — time field explicitly includes afterschool or before school
    if any(t in time for t in ['Afterschool', 'Before School']):
        return 'CONFIRMED_OST'

    # Explicit non-OST time values
    if time in NOT_OST_TIMES:
        return 'NOT_OST'

    # NaN time — categorize by organization
    if time == '':
        if any(no in org for no in NOT_OST_ORGS):
            return 'NOT_OST'
        if org in all_inferred_ost_orgs:
            return 'NaN_INFERRED_OST'
        return 'NaN_UNVERIFIED'

    # Anything remaining needs review
    return 'OTHER'

partners['OST_CATEGORY'] = partners.apply(categorize_ost, axis=1)

print("\nOST Category counts:")
print(partners['OST_CATEGORY'].value_counts().to_string())

# Flag any OTHER for review — should be zero
other = partners[partners['OST_CATEGORY'] == 'OTHER']
if len(other) > 0:
    print(f"\nWARNING: {len(other)} records still OTHER — review before proceeding:")
    print(other[['Organization Name:', 'Time', 'Program Areas:']].to_string())
else:
    print("\nNo OTHER records — categorization complete")

# ==========================================
# GRADE BAND FLAGS — PROGRAM LEVEL
# Based on Grades Served: field
# ==========================================
partners['PROG_PREK'] = partners['Grades Served:'].apply(
    lambda g: bool(parse_program_grades(g) & PREK_GRADES)
)
partners['PROG_ELEM'] = partners['Grades Served:'].apply(
    lambda g: bool(parse_program_grades(g) & ELEM_GRADES)
)
partners['PROG_MIDDLE'] = partners['Grades Served:'].apply(
    lambda g: bool(parse_program_grades(g) & MIDDLE_GRADES)
)

# Programs with no grade information — cannot assign to any band
no_grades = (~partners['PROG_PREK'] & 
             ~partners['PROG_ELEM'] & 
             ~partners['PROG_MIDDLE'])

print(f"\nProgram-level grade band coverage:")
print(f"  Pre-K:              {partners['PROG_PREK'].sum()}")
print(f"  Elementary:         {partners['PROG_ELEM'].sum()}")
print(f"  Middle:             {partners['PROG_MIDDLE'].sum()}")
print(f"  No grade info:      {no_grades.sum()}")

# ==========================================
# SCHOOL APPLICABLE BANDS
# From shapefile GRADES field — determines which bands
# each school is eligible to be ranked on
# ==========================================
school_lookup = schools[['SCHID', 'NAME', 'RC_CODE', 'GRADES']].copy()

# Parse applicable bands from GRADES field
bands = school_lookup['GRADES'].apply(school_applicable_bands)
school_lookup['SCHOOL_PREK']   = bands.apply(lambda x: x['prek'])
school_lookup['SCHOOL_ELEM']   = bands.apply(lambda x: x['elem'])
school_lookup['SCHOOL_MIDDLE'] = bands.apply(lambda x: x['middle'])

# RC_CODE is int in schools file
school_lookup['RC_CODE'] = pd.to_numeric(
    school_lookup['RC_CODE'], errors='coerce'
).astype('Int64')

print(f"\nSchool band applicability:")
print(f"  Schools serving Pre-K:       {school_lookup['SCHOOL_PREK'].sum()}")
print(f"  Schools serving Elementary:  {school_lookup['SCHOOL_ELEM'].sum()}")
print(f"  Schools serving Middle:      {school_lookup['SCHOOL_MIDDLE'].sum()}")

# ==========================================
# JOIN PARTNERS TO SCHOOLS VIA RC CODE
# RC in partners is float (101401.0) → cast to nullable int
# ==========================================

partners['RC_INT'] = pd.to_numeric(
    partners['RC'].astype(str).str.strip(), errors='coerce'
).astype('Int64')

PARTNER_RC_CORRECTIONS = {
    101394: 101420,  # Sarah Roberts Elementary — outdated RC in Partners file
                     # Confirmed via OI file: Roberts Elementary = 101420
}

partners['RC_INT'] = partners['RC_INT'].replace(PARTNER_RC_CORRECTIONS)
print(f"\nRC corrections applied: {len(PARTNER_RC_CORRECTIONS)}")
print(f"  101394 → 101420 (Sarah Roberts Elementary)")

before_join = len(partners)
partners = partners.merge(
    school_lookup[[
        'SCHID', 'NAME', 'RC_CODE',
        'SCHOOL_PREK', 'SCHOOL_ELEM', 'SCHOOL_MIDDLE'
    ]],
    left_on='RC_INT',
    right_on='RC_CODE',
    how='left'
)

matched   = partners['SCHID'].notna().sum()
unmatched = partners['SCHID'].isna().sum()
print(f"\nSchool join:")
print(f"  Matched to school: {matched}/{before_join}")
print(f"  Unmatched:         {unmatched}")

if unmatched > 0:
    print("\n  Unmatched programs (no RC or RC not in school layer):")
    print(partners[partners['SCHID'].isna()][
        ['School Name:', 'Organization Name:', 'RC', 'OST_CATEGORY']
    ].head(10).to_string())

# ==========================================
# OUTPUT 1: Partners_OST.csv
# Confirmed + inferred OST only
# Used for gap ranking
# ==========================================
ost_mask    = partners['OST_CATEGORY'].isin(['CONFIRMED_OST', 'NaN_INFERRED_OST'])
partners_ost = partners[ost_mask].copy()

ost_cols = [
    'SCHID', 'NAME', 'RC_CODE',
    'School Name:', 'Organization Name:', 'Program Name:',
    'Time', 'OST_CATEGORY',
    'Grades Served:', 'PROG_PREK', 'PROG_ELEM', 'PROG_MIDDLE',
    'SCHOOL_PREK', 'SCHOOL_ELEM', 'SCHOOL_MIDDLE',
    'Program Areas:', 'Days of Operation:',
    'Student Fees?', 'Service Capacity',
]
ost_cols = [c for c in ost_cols if c in partners_ost.columns]
partners_ost[ost_cols].to_csv('Partners_OST.csv', index=False)
print(f"\nSaved Partners_OST.csv — {len(partners_ost)} records")

# ==========================================
# OUTPUT 2: Partners_All.csv
# All records including unverified
# Used for principal view
# ==========================================
all_cols = [
    'SCHID', 'NAME', 'RC_CODE',
    'School Name:', 'Organization Name:', 'Website:_1',
    'Program Name:', 'Program Description:',
    'Time', 'OST_CATEGORY',
    'Grades Served:', 'PROG_PREK', 'PROG_ELEM', 'PROG_MIDDLE',
    'SCHOOL_PREK', 'SCHOOL_ELEM', 'SCHOOL_MIDDLE',
    'Program Areas:', 'Program Subareas:',
    'Days of Operation:', 'Student Fees?',
    'Explanation of Student Fees', 'Service Capacity',
]
all_cols = [c for c in all_cols if c in partners.columns]
partners[all_cols].to_csv('Partners_All.csv', index=False)
print(f"Saved Partners_All.csv — {len(partners)} records")

# ==========================================
# OUTPUT 3: Partners_OST_Summary.csv
# Per-school OST partner counts by band
# Used as input to compute_rankings.py
# ==========================================
ost_summary = partners_ost.groupby('SCHID').agg(
    OST_TOTAL_CNT  = ('Organization Name:', 'count'),
    OST_PREK_CNT   = ('PROG_PREK',   'sum'),
    OST_ELEM_CNT   = ('PROG_ELEM',   'sum'),
    OST_MIDDLE_CNT = ('PROG_MIDDLE', 'sum'),
).reset_index()

ost_summary.to_csv('Partners_OST_Summary.csv', index=False)

no_partners = len(schools) - len(ost_summary)
print(f"Saved Partners_OST_Summary.csv — {len(ost_summary)} schools with OST partners")
print(f"Schools with zero OST partners: {no_partners}")

print(f"\nOST partner count distribution:")
print(ost_summary['OST_TOTAL_CNT'].describe().round(1).to_string())

print(f"\nBand-specific coverage:")
print(f"  Schools with Pre-K OST partners:    "
      f"{(ost_summary['OST_PREK_CNT'] > 0).sum()}")
print(f"  Schools with Elementary OST partners: "
      f"{(ost_summary['OST_ELEM_CNT'] > 0).sum()}")
print(f"  Schools with Middle OST partners:   "
      f"{(ost_summary['OST_MIDDLE_CNT'] > 0).sum()}")
