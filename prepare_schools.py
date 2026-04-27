import pandas as pd
import geopandas as gpd

# ==========================================
# LOAD SCHOOLS SHAPEFILE
# ==========================================
print("Loading schools shapefile...")
schools = gpd.read_file('SCHOOLS_PT.shp')
schools = schools[schools['DIST_CODE'] == '00350000'].copy()
print(f"  BPS schools: {len(schools)}")

# ==========================================
# LOAD AND JOIN ENROLLMENT
# Filter to SY2026 and individual schools only
# Strip commas from count fields, % from pct fields
# ==========================================
print("\nLoading enrollment...")
enroll = pd.read_csv(
    'Enrollment__Grade,_Race_Ethnicity,_Gender,_and_Selected_Populations_20260306.csv',
    dtype=str
)
enroll = enroll[
    (enroll['DIST_CODE'] == '00350000') &
    (enroll['ORG_CODE']  != '00350000') &
    (enroll['SY']        == '2026')
].copy()
print(f"  BPS school enrollment rows (SY2026): {len(enroll)}")

count_cols = [
    'TOTAL_CNT','PK_CNT','K_CNT','G1_CNT','G2_CNT','G3_CNT',
    'G4_CNT','G5_CNT','G6_CNT','G7_CNT','G8_CNT','G9_CNT',
    'G10_CNT','G11_CNT','G12_CNT','SP_CNT',
    'EL_CNT','FLNE_CNT','HN_CNT','LI_CNT','ECD_CNT','SWD_CNT'
]
pct_cols = [
    'AIAN_PCT','AS_PCT','BAA_PCT','HL_PCT','MNHL_PCT','NHPI_PCT',
    'WH_PCT','FE_PCT','MA_PCT','NB_PCT','EL_PCT','FLNE_PCT',
    'HN_PCT','LI_PCT','ECD_PCT','SWD_PCT'
]

for col in count_cols:
    if col in enroll.columns:
        enroll[col] = pd.to_numeric(
            enroll[col].str.replace(',', '', regex=False),
            errors='coerce'
        )

for col in pct_cols:
    if col in enroll.columns:
        enroll[col] = pd.to_numeric(
            enroll[col].str.replace('%', '', regex=False),
            errors='coerce'
        )

# Grade band enrollment totals
enroll['ENR_PREK']   = enroll['PK_CNT']
enroll['ENR_ELEM']   = enroll[
    ['K_CNT','G1_CNT','G2_CNT','G3_CNT','G4_CNT','G5_CNT']
].sum(axis=1)
enroll['ENR_MIDDLE'] = enroll[
    ['G6_CNT','G7_CNT','G8_CNT']
].sum(axis=1)

# Build enroll_keep without duplicates, preserving order
# TOTAL_CNT appears in both the explicit list and count_cols — deduplicate here
enroll_keep = list(dict.fromkeys(
    ['ORG_CODE', 'ORG_NAME', 'TOTAL_CNT',
     'ENR_PREK', 'ENR_ELEM', 'ENR_MIDDLE'] +
    count_cols + pct_cols
))
enroll_keep = [c for c in enroll_keep if c in enroll.columns]
enroll = enroll[enroll_keep]

# Drop DIST_CODE and DIST_NAME from enrollment before merge
# — these already exist in the shapefile
enroll = enroll.drop(
    columns=[c for c in ['DIST_CODE','DIST_NAME'] if c in enroll.columns]
)

before = len(schools)
schools = schools.merge(enroll, left_on='SCHID', right_on='ORG_CODE', how='left')
matched_enroll = schools['TOTAL_CNT'].notna().sum()
print(f"  Enrollment join: {matched_enroll}/{before} matched")

# ==========================================
# LOAD OI SCORES
# ==========================================
print("\nLoading OI scores...")
oi = pd.read_csv(
    'Boston Public Schools Opportunity Index (OI) Scores_Public_Website'
    ' - Most Recent OI Scores.csv'
)
print(f"  OI records: {len(oi)}")

# Load name crosswalk
# Handles 11 schools where shapefile name differs from OI name
# Henderson Upper has no OI entry — documented as empty OI_NAME
crosswalk = pd.read_csv('name_crosswalk.csv')
crosswalk_dict = {}
for _, row in crosswalk.iterrows():
    oi_name = row['OI_NAME']
    crosswalk_dict[row['SHP_NAME']] = (
        '' if pd.isna(oi_name) else str(oi_name).strip()
    )

def normalize(name):
    return (str(name)
            .lower()
            .strip()
            .replace('school', '')
            .replace('  ', ' ')
            .strip())

oi['NAME_NORM'] = oi['School Name'].apply(normalize)
oi_lookup = dict(
    zip(oi['NAME_NORM'], zip(oi['RC Code'], oi['FY27 OI Score']))
)

matched_oi    = 0
no_oi_entry   = 0
no_name_match = 0

rc_codes         = []
oi_scores        = []
oi_names_matched = []

for _, row in schools.iterrows():
    shp_name = row['NAME']

    # Apply crosswalk if this school has a known name discrepancy
    lookup_name = crosswalk_dict.get(shp_name, shp_name)

    # Empty string = documented no OI entry (Henderson Upper)
    if pd.isna(lookup_name) or str(lookup_name).strip() == '':
        rc_codes.append(None)
        oi_scores.append(None)
        oi_names_matched.append('No OI entry')
        no_oi_entry += 1
        continue

    norm = normalize(lookup_name)
    if norm in oi_lookup:
        rc, score = oi_lookup[norm]
        rc_codes.append(int(rc))
        oi_scores.append(score)
        oi_names_matched.append(lookup_name)
        matched_oi += 1
    else:
        rc_codes.append(None)
        oi_scores.append(None)
        oi_names_matched.append('No match')
        no_name_match += 1

schools['RC_CODE']         = rc_codes
schools['BPS_OI_SCORE']    = oi_scores
schools['OI_NAME_MATCHED'] = oi_names_matched

print(f"  OI score join: {matched_oi}/105 matched")
print(f"  No OI entry (documented): {no_oi_entry}")
print(f"  No match found:           {no_name_match}")

if no_name_match > 0:
    print("\n  Unmatched schools — add to name_crosswalk.csv if fixable:")
    unmatched = schools[schools['OI_NAME_MATCHED'] == 'No match']['NAME']
    print(unmatched.to_string())

# ==========================================
# FINAL COLUMN CHECK
# ==========================================
dupes = schools.columns[schools.columns.duplicated()].tolist()
if dupes:
    print(f"\nWARNING: Duplicate columns found and removed: {dupes}")
    schools = schools.loc[:, ~schools.columns.duplicated()]
else:
    print("\nNo duplicate columns — clean to save")

# ==========================================
# SELECT OUTPUT COLUMNS
# ==========================================
output_cols = [
    'SCHID', 'NAME', 'ADDRESS', 'TOWN', 'ZIPCODE',
    'GRADES', 'TYPE_DESC',
    'TOTAL_CNT', 'ENR_PREK', 'ENR_ELEM', 'ENR_MIDDLE',
    'EL_PCT', 'LI_PCT', 'LI_CNT', 'SWD_PCT',
    'HL_PCT', 'BAA_PCT',
    'RC_CODE', 'BPS_OI_SCORE', 'OI_NAME_MATCHED',
    'geometry'
]
output_cols = [c for c in output_cols if c in schools.columns]
schools_out = schools[output_cols]

# ==========================================
# SAVE
# ==========================================
schools_out.to_file('BPS_Schools.gpkg', driver='GPKG')
print(f"\nSaved BPS_Schools.gpkg")
print(f"  Records: {len(schools_out)}")
print(f"  Fields:  {[c for c in output_cols if c != 'geometry']}")