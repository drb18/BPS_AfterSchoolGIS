import pandas as pd
import geopandas as gpd

# ==========================================
# LOAD DATA
# ==========================================
print("Loading data...")
schools    = gpd.read_file('BPS_Schools.gpkg')
isochrones = gpd.read_file('BPS_Isochrones.gpkg')
eec        = pd.read_csv('EEC_Center_Clean.csv',
                          encoding='utf-8-sig', low_memory=False)
partners   = pd.read_csv('Partners_OST_Summary.csv', dtype=str)

print(f"  Schools:         {len(schools)}")
print(f"  Isochrones:      {len(isochrones)}")
print(f"  EEC centers:     {len(eec)}")
print(f"  Partner summary: {len(partners)}")
print(f"\n  Schools CRS:    {schools.crs}")
print(f"  Isochrones CRS: {isochrones.crs}")

# Align CRS
if schools.crs != isochrones.crs:
    print("  Reprojecting schools to match isochrones CRS...")
    schools = schools.to_crs(isochrones.crs)

# ==========================================
# SCHOOL APPLICABLE BANDS
# Pre-K:       school has PK in GRADES
# Elementary:  school has K or 01-05
# Middle:      school has 06-08
# ==========================================
def school_applicable_bands(grades_field):
    if pd.isna(grades_field):
        return {'prek': False, 'elem': False, 'middle': False}
    parts = set(g.strip() for g in str(grades_field).split(','))
    return {
        'prek':   'PK' in parts,
        'elem':   bool(parts & {'K', '01', '02', '03', '04', '05'}),
        'middle': bool(parts & {'06', '07', '08'}),
    }

bands = schools['GRADES'].apply(school_applicable_bands)
schools['SCHOOL_PREK']   = bands.apply(lambda x: x['prek'])
schools['SCHOOL_ELEM']   = bands.apply(lambda x: x['elem'])
schools['SCHOOL_MIDDLE'] = bands.apply(lambda x: x['middle'])

print(f"\nSchool band applicability:")
print(f"  Pre-K:       {schools['SCHOOL_PREK'].sum()}")
print(f"  Elementary:  {schools['SCHOOL_ELEM'].sum()}")
print(f"  Middle:      {schools['SCHOOL_MIDDLE'].sum()}")

# ==========================================
# CONVERT EEC TO GEODATAFRAME
# ==========================================
eec_gdf = gpd.GeoDataFrame(
    eec,
    geometry=gpd.points_from_xy(eec['Longitude'], eec['Latitude']),
    crs='EPSG:4326'
).to_crs(isochrones.crs)

# ==========================================
# STEP 1: SCHOOL SHARE COUNT
# For each EEC program: how many school
# isochrones contain it?
# Denominator for adjusted capacity.
# ==========================================
print("\nComputing school share counts for EEC programs...")

eec_in_iso = gpd.sjoin(
    eec_gdf[['PROVIDER_NUMBER', 'geometry']],
    isochrones[['SCHID', 'geometry']],
    how='inner',
    predicate='within'
)

share_counts = (eec_in_iso
                .groupby('PROVIDER_NUMBER')
                .size()
                .reset_index(name='SCHOOL_SHARE_COUNT'))

eec_gdf = eec_gdf.merge(share_counts, on='PROVIDER_NUMBER', how='left')
eec_gdf['SCHOOL_SHARE_COUNT'] = eec_gdf['SCHOOL_SHARE_COUNT'].fillna(0)

in_iso     = (eec_gdf['SCHOOL_SHARE_COUNT'] > 0).sum()
out_iso    = (eec_gdf['SCHOOL_SHARE_COUNT'] == 0).sum()
mean_share = (eec_gdf[eec_gdf['SCHOOL_SHARE_COUNT'] > 0]
              ['SCHOOL_SHARE_COUNT'].mean())

print(f"  Within at least one isochrone: {in_iso}/{len(eec_gdf)}")
print(f"  Outside all isochrones:        {out_iso}")
print(f"  Mean schools sharing a program: {mean_share:.1f}")

# Adjusted capacity
# Programs outside all isochrones contribute 0
eec_gdf['ADJ_CAPACITY'] = eec_gdf.apply(
    lambda r: float(r['LICENSED_CAPACITY']) / r['SCHOOL_SHARE_COUNT']
    if r['SCHOOL_SHARE_COUNT'] > 0 else 0.0,
    axis=1
)

# ==========================================
# STEP 2: ADJUSTED CAPACITY BY SCHOOL/BAND
# ==========================================
print("\nComputing adjusted capacity by school and band...")

eec_active = eec_gdf[eec_gdf['SCHOOL_SHARE_COUNT'] > 0].copy()

eec_school = gpd.sjoin(
    eec_active[['PROVIDER_NUMBER', 'LICENSED_CAPACITY', 'ADJ_CAPACITY',
                'SERVES_PREK', 'SERVES_ELEM', 'SERVES_MIDDLE', 'geometry']],
    isochrones[['SCHID', 'geometry']],
    how='inner',
    predicate='within'
)
eec_school = eec_school.drop(columns=['index_right'], errors='ignore')

for band in ['PREK', 'ELEM', 'MIDDLE']:
    serves_col = f'SERVES_{band}'
    band_df    = eec_school[eec_school[serves_col] == True]

    cap = (band_df.groupby('SCHID')['ADJ_CAPACITY']
           .sum()
           .reset_index(name=f'EEC_ADJ_CAP_{band}'))

    cnt = (band_df.groupby('SCHID')['PROVIDER_NUMBER']
           .nunique()
           .reset_index(name=f'EEC_RAW_CNT_{band}'))

    schools = schools.merge(cap, on='SCHID', how='left')
    schools = schools.merge(cnt, on='SCHID', how='left')
    schools[f'EEC_ADJ_CAP_{band}'] = (schools[f'EEC_ADJ_CAP_{band}']
                                       .fillna(0))
    schools[f'EEC_RAW_CNT_{band}'] = (schools[f'EEC_RAW_CNT_{band}']
                                       .fillna(0))

    print(f"  {band}: "
          f"{(schools[f'EEC_RAW_CNT_{band}'] > 0).sum()} schools "
          f"have at least one EEC program in isochrone")

# ==========================================
# STEP 3: JOIN PARTNER OST COUNTS
# ==========================================
print("\nJoining partner OST counts...")

for col in ['OST_TOTAL_CNT','OST_PREK_CNT',
            'OST_ELEM_CNT','OST_MIDDLE_CNT']:
    partners[col] = pd.to_numeric(
        partners[col], errors='coerce'
    ).fillna(0)

schools = schools.merge(
    partners[['SCHID','OST_TOTAL_CNT',
              'OST_PREK_CNT','OST_ELEM_CNT','OST_MIDDLE_CNT']],
    on='SCHID', how='left'
)
for col in ['OST_TOTAL_CNT','OST_PREK_CNT',
            'OST_ELEM_CNT','OST_MIDDLE_CNT']:
    schools[col] = schools[col].fillna(0)

print(f"  Schools with ≥1 OST partner: "
      f"{(schools['OST_TOTAL_CNT'] > 0).sum()}/105")

# ==========================================
# STEP 4: NEED SCORE
# LI_PCT = Low Income percentage
# Replaces ECD_PCT which is not reported
# at school level in MA enrollment data
# NEED_SCORE = TOTAL_CNT x (LI_PCT / 100)
# ==========================================
schools['TOTAL_CNT'] = pd.to_numeric(
    schools['TOTAL_CNT'], errors='coerce'
)
schools['LI_PCT'] = pd.to_numeric(
    schools['LI_PCT'], errors='coerce'
)
schools['LI_CNT'] = pd.to_numeric(
    schools['LI_CNT'], errors='coerce'
)
schools['NEED_SCORE'] = (
    schools['TOTAL_CNT'] * (schools['LI_PCT'] / 100)
)

print(f"\nNeed score summary:")
print(schools['NEED_SCORE'].describe().round(1).to_string())

# ==========================================
# STEP 5: GAP TIER CLASSIFICATION
# Applied after computing GAP_SEVERITY
# Thresholds match legend categories in QGIS
# ==========================================
def gap_tier(severity):
    if pd.isna(severity):
        return 'Not applicable'
    if severity >= 0.70:
        return 'High Concern'
    if severity >= 0.42:
        return 'Moderate-High Concern'
    if severity >= 0.12:
        return 'Moderate Concern'
    return 'Lower Concern'

# ==========================================
# STEP 6: RANK BY BAND
#
# Three component ranks per eligible school:
#   RANK_NEED: rank descending on NEED_SCORE
#     highest need = rank 1
#   RANK_OST:  rank ascending on OST partner count
#     fewest partners = rank 1
#   RANK_EEC:  rank ascending on adjusted EEC capacity
#     least capacity = rank 1
#
# COMPOSITE = sum of three ranks
#   lower composite = more gap concern
#
# GAP_SEVERITY = 1 - percentile_rank(COMPOSITE)
#   0 to 1; higher = more concerning
#
# GAP_RANK = ordinal rank within eligible schools
#   rank 1 = most concerning
#
# GAP_ELIGIBLE = total eligible schools for band
#   denominator for rank display
#
# GAP_TIER = qualitative label
# ==========================================
print("\nComputing rankings by band...")

BAND_CONFIG = {
    'PREK':   ('SCHOOL_PREK',   'OST_PREK_CNT',   'EEC_ADJ_CAP_PREK'),
    'ELEM':   ('SCHOOL_ELEM',   'OST_ELEM_CNT',   'EEC_ADJ_CAP_ELEM'),
    'MIDDLE': ('SCHOOL_MIDDLE', 'OST_MIDDLE_CNT', 'EEC_ADJ_CAP_MIDDLE'),
}

for band, (applicable_col, ost_col, eec_col) in BAND_CONFIG.items():
    eligible = schools[schools[applicable_col] == True].copy()
    n        = len(eligible)

    if n == 0:
        print(f"  {band}: no eligible schools — skipping")
        continue

    eligible[f'RANK_NEED_{band}'] = eligible['NEED_SCORE'].rank(
        ascending=False, method='min', na_option='bottom'
    )
    eligible[f'RANK_OST_{band}'] = eligible[ost_col].rank(
        ascending=True, method='min', na_option='bottom'
    )
    eligible[f'RANK_EEC_{band}'] = eligible[eec_col].rank(
        ascending=True, method='min', na_option='bottom'
    )
    eligible[f'COMPOSITE_{band}'] = (
        eligible[f'RANK_NEED_{band}'] +
        eligible[f'RANK_OST_{band}'] +
        eligible[f'RANK_EEC_{band}']
    )

    # GAP_SEVERITY: 1 = most concerning, 0 = least concerning
    eligible[f'GAP_SEVERITY_{band}'] = (
        1 - eligible[f'COMPOSITE_{band}'].rank(
            ascending=True, pct=True, method='average'
        )
    )

    # Ordinal rank: 1 = most concerning
    eligible[f'GAP_RANK_{band}'] = (
        eligible[f'COMPOSITE_{band}']
        .rank(ascending=True, method='min')
        .astype('Int64')
    )

    # Total eligible schools — denominator for rank display
    eligible[f'GAP_ELIGIBLE_{band}'] = n

    # Qualitative tier
    eligible[f'GAP_TIER_{band}'] = (
        eligible[f'GAP_SEVERITY_{band}'].apply(gap_tier)
    )

    rank_cols = [
        f'RANK_NEED_{band}',    f'RANK_OST_{band}',
        f'RANK_EEC_{band}',     f'COMPOSITE_{band}',
        f'GAP_SEVERITY_{band}', f'GAP_RANK_{band}',
        f'GAP_ELIGIBLE_{band}', f'GAP_TIER_{band}',
    ]

    schools = schools.merge(
        eligible[['SCHID'] + rank_cols],
        on='SCHID', how='left'
    )

    print(f"\n  {band}: {n} eligible schools")
    print(f"    Composite range: "
          f"{eligible[f'COMPOSITE_{band}'].min():.0f} – "
          f"{eligible[f'COMPOSITE_{band}'].max():.0f}")
    print(f"    Top 5 most concerning:")
    top5 = (eligible
            .nsmallest(5, f'COMPOSITE_{band}')
            [['NAME',
              f'RANK_NEED_{band}', f'RANK_OST_{band}',
              f'RANK_EEC_{band}',  f'COMPOSITE_{band}',
              f'GAP_RANK_{band}',  f'GAP_TIER_{band}']])
    print(top5.to_string())

# ==========================================
# STEP 7: PRIMARY GAP BAND
# Band with highest GAP_SEVERITY per school
# Used as primary color variable on map
# ==========================================
def primary_gap_band(row):
    candidates = []
    for band in ['PREK', 'ELEM', 'MIDDLE']:
        if not row.get(f'SCHOOL_{band}', False):
            continue
        severity = row.get(f'GAP_SEVERITY_{band}')
        if pd.notna(severity):
            candidates.append((band, severity))
    if not candidates:
        return 'Not applicable'
    return max(candidates, key=lambda x: x[1])[0]

schools['PRIMARY_GAP_BAND'] = schools.apply(primary_gap_band, axis=1)

# Primary gap tier — tier for the primary gap band
schools['PRIMARY_GAP_TIER'] = schools.apply(
    lambda row: row.get(
        f"GAP_TIER_{row['PRIMARY_GAP_BAND']}", 'Not applicable'
    ) if row['PRIMARY_GAP_BAND'] != 'Not applicable'
    else 'Not applicable',
    axis=1
)

# Primary gap rank display string
# Format: "Ranked 5 of 72 Pre-K schools (High Concern)"
def primary_gap_rank_string(row):
    band = row.get('PRIMARY_GAP_BAND')
    if band == 'Not applicable' or pd.isna(band):
        return 'Not applicable'
    rank     = row.get(f'GAP_RANK_{band}')
    eligible = row.get(f'GAP_ELIGIBLE_{band}')
    tier     = row.get(f'GAP_TIER_{band}', '')
    band_label = {'PREK': 'Pre-K',
                  'ELEM': 'Elementary',
                  'MIDDLE': 'Middle'}.get(band, band)
    if pd.isna(rank):
        return 'Not applicable'
    return f"Ranked {int(rank)} of {int(eligible)} {band_label} schools ({tier})"

schools['PRIMARY_GAP_LABEL'] = schools.apply(
    primary_gap_rank_string, axis=1
)

print(f"\nPrimary gap band distribution:")
print(schools['PRIMARY_GAP_BAND'].value_counts().to_string())

print(f"\nPrimary gap tier distribution:")
print(schools['PRIMARY_GAP_TIER'].value_counts().to_string())

# ==========================================
# STEP 8: ZERO-COVERAGE FLAGS
# ==========================================
schools['ZERO_EEC_PREK']   = (schools['SCHOOL_PREK']   &
                               (schools['EEC_RAW_CNT_PREK']   == 0))
schools['ZERO_EEC_ELEM']   = (schools['SCHOOL_ELEM']   &
                               (schools['EEC_RAW_CNT_ELEM']   == 0))
schools['ZERO_EEC_MIDDLE'] = (schools['SCHOOL_MIDDLE'] &
                               (schools['EEC_RAW_CNT_MIDDLE'] == 0))
schools['ZERO_OST_ANY']    = (schools['OST_TOTAL_CNT'] == 0)

print(f"\nZero-coverage flags:")
print(f"  No EEC in isochrone — Pre-K applicable:    "
      f"{schools['ZERO_EEC_PREK'].sum()}")
print(f"  No EEC in isochrone — Elem applicable:     "
      f"{schools['ZERO_EEC_ELEM'].sum()}")
print(f"  No EEC in isochrone — Middle applicable:   "
      f"{schools['ZERO_EEC_MIDDLE'].sum()}")
print(f"  No OST partners at all:                    "
      f"{schools['ZERO_OST_ANY'].sum()}")

# ==========================================
# STEP 9: SAVE GEOPACKAGE
# ==========================================
schools.to_file('BPS_Schools_Ranked.gpkg', driver='GPKG')
print(f"\nSaved BPS_Schools_Ranked.gpkg — {len(schools)} records")

# Confirm new fields present
new_fields = [
    'GAP_RANK_PREK',     'GAP_ELIGIBLE_PREK',     'GAP_TIER_PREK',
    'GAP_RANK_ELEM',     'GAP_ELIGIBLE_ELEM',     'GAP_TIER_ELEM',
    'GAP_RANK_MIDDLE',   'GAP_ELIGIBLE_MIDDLE',   'GAP_TIER_MIDDLE',
    'PRIMARY_GAP_BAND',  'PRIMARY_GAP_TIER',      'PRIMARY_GAP_LABEL',
]
print("\nNew fields confirmed in output:")
for f in new_fields:
    present = f in schools.columns
    sample  = schools[f].iloc[0] if present else 'MISSING'
    print(f"  {f}: {sample}")

# ==========================================
# STEP 10: EXPORT RANKED CSVs
# One per band, sorted most to least concerning
# ==========================================
for band in ['PREK', 'ELEM', 'MIDDLE']:
    applicable_col = f'SCHOOL_{band}'
    composite_col  = f'COMPOSITE_{band}'

    if composite_col not in schools.columns:
        continue

    band_df = (schools[schools[applicable_col] == True]
               .sort_values(composite_col, ascending=True)
               .copy())

    band_label = {'PREK': 'Pre-K',
                  'ELEM': 'Elementary',
                  'MIDDLE': 'Middle'}[band]

    out_cols = [
        'SCHID', 'NAME', 'TOWN',
        'NEED_SCORE', 'TOTAL_CNT', 'LI_PCT',
        f'OST_{band}_CNT',
        f'EEC_ADJ_CAP_{band}', f'EEC_RAW_CNT_{band}',
        f'RANK_NEED_{band}',   f'RANK_OST_{band}',
        f'RANK_EEC_{band}',    composite_col,
        f'GAP_RANK_{band}',    f'GAP_ELIGIBLE_{band}',
        f'GAP_SEVERITY_{band}',f'GAP_TIER_{band}',
        'BPS_OI_SCORE',
    ]
    out_cols = [c for c in out_cols if c in band_df.columns]
    band_df[out_cols].to_csv(f'Rankings_{band}.csv', index=False)

    print(f"\nSaved Rankings_{band}.csv — {len(band_df)} schools")
    print(f"  Top 5 most concerning ({band_label}):")
    print(band_df[['NAME', f'GAP_RANK_{band}',
                   f'GAP_ELIGIBLE_{band}',
                   f'GAP_TIER_{band}',
                   'NEED_SCORE', 'LI_PCT']
                 ].head(5).to_string())