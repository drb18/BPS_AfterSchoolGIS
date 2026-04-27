# produce_rankings.py
# Reads BPS_Schools_Ranked.gpkg and produces
# ranking CSVs for each grade band plus a
# combined summary across all bands.
# Output: Rankings_Summary_PREK.csv
#         Rankings_Summary_ELEM.csv
#         Rankings_Summary_MIDDLE.csv
#         Rankings_Summary_All.csv

import pandas as pd
import geopandas as gpd

# ==========================================
# LOAD
# ==========================================
print("Loading BPS_Schools_Ranked.gpkg...")
schools = gpd.read_file('BPS_Schools_Ranked.gpkg')
print(f"  Loaded: {len(schools)} schools")

# Drop geometry for tabular output
df = pd.DataFrame(schools.drop(columns='geometry'))

# ==========================================
# BAND CONFIGURATION
# ==========================================
BANDS = {
    'PREK':   'Pre-K',
    'ELEM':   'Elementary',
    'MIDDLE': 'Middle',
}

# ==========================================
# PRODUCE ONE CSV PER BAND
# Includes only schools eligible for that band
# Sorted by GAP_RANK (1 = most concerning)
# ==========================================
for band_code, band_label in BANDS.items():

    applicable_col  = f'SCHOOL_{band_code}'
    rank_need_col   = f'RANK_NEED_{band_code}'
    rank_ost_col    = f'RANK_OST_{band_code}'
    rank_eec_col    = f'RANK_EEC_{band_code}'
    composite_col   = f'COMPOSITE_{band_code}'
    gap_rank_col    = f'GAP_RANK_{band_code}'
    gap_tier_col    = f'GAP_TIER_{band_code}'
    gap_eligible_col= f'GAP_ELIGIBLE_{band_code}'
    ost_cnt_col     = f'OST_{band_code}_CNT'
    eec_adj_col     = f'EEC_ADJ_CAP_{band_code}'
    eec_raw_col     = f'EEC_RAW_CNT_{band_code}'
    enr_col         = f'ENR_{band_code}'
    zero_eec_col    = f'ZERO_EEC_{band_code}'

    # Filter to eligible schools only
    eligible = df[df[applicable_col] == True].copy()
    n = len(eligible)

    # Sort by gap rank
    eligible = eligible.sort_values(gap_rank_col, ascending=True)

    # Build clean output
    out = pd.DataFrame()
    out['Gap_Rank']          = eligible[gap_rank_col].astype('Int64')
    out['SCHID']             = eligible['SCHID']
    out['School_Name']       = eligible['NAME']
    out['Town']              = eligible['TOWN']
    out['School_Type']       = eligible['TYPE_DESC']
    out['Grades']            = eligible['GRADES']
    out[f'Enrollment_{band_label}'] = eligible[enr_col].astype('Int64')
    out['Total_Enrollment']  = eligible['TOTAL_CNT'].astype('Int64')
    out['Low_Income_Pct']    = eligible['LI_PCT'].round(1)
    out['Low_Income_Cnt']    = eligible['LI_CNT'].astype('Int64')
    out['Need_Score']        = eligible['NEED_SCORE'].round(1)
    out['Rank_Need']         = eligible[rank_need_col].astype('Int64')
    out[f'OST_Partners_{band_label}'] = eligible[ost_cnt_col].astype('Int64')
    out['Rank_OST_Partners'] = eligible[rank_ost_col].astype('Int64')
    out['EEC_Programs_In_Isochrone'] = eligible[eec_raw_col].astype('Int64')
    out['EEC_Adj_Capacity']  = eligible[eec_adj_col].round(1)
    out['Rank_EEC_Capacity'] = eligible[rank_eec_col].astype('Int64')
    out['Composite_Score']   = eligible[composite_col].astype('Int64')
    out['Gap_Tier']          = eligible[gap_tier_col]
    out['Eligible_Schools']  = n
    out['Zero_EEC_Coverage'] = eligible[zero_eec_col].map(
        {True: 'Yes', False: 'No', 1: 'Yes', 0: 'No'}
    )
    out['Zero_OST_Partners'] = eligible['ZERO_OST_ANY'].map(
        {True: 'Yes', False: 'No', 1: 'Yes', 0: 'No'}
    )
    out['BPS_OI_Score']      = eligible['BPS_OI_SCORE'].round(3)

    filename = f'Rankings_Summary_{band_code}.csv'
    out.to_csv(filename, index=False)

    print(f"\nSaved {filename} — {n} schools")
    print(f"  Band: {band_label}")
    print(f"  Top 10 most concerning:")
    print(out[['Gap_Rank', 'School_Name',
               'Rank_Need', 'Rank_OST_Partners',
               'Rank_EEC_Capacity', 'Composite_Score',
               'Gap_Tier']].head(10).to_string(index=False))

# ==========================================
# COMBINED SUMMARY — ALL BANDS
# One row per school
# Shows applicable bands and worst rank
# Useful for district-level overview
# ==========================================
print("\nBuilding combined summary...")

summary = pd.DataFrame()
summary['SCHID']           = df['SCHID']
summary['School_Name']     = df['NAME']
summary['Town']            = df['TOWN']
summary['School_Type']     = df['TYPE_DESC']
summary['Grades']          = df['GRADES']
summary['Total_Enrollment']= df['TOTAL_CNT'].astype('Int64')
summary['Low_Income_Pct']  = df['LI_PCT'].round(1)
summary['Need_Score']      = df['NEED_SCORE'].round(1)
summary['OST_Partners_Total'] = df['OST_TOTAL_CNT'].astype('Int64')
summary['Zero_OST_Partners']  = df['ZERO_OST_ANY'].map(
    {True: 'Yes', False: 'No', 1: 'Yes', 0: 'No'}
)

# Applicable band flags
summary['Serves_PreK']     = df['SCHOOL_PREK'].map(
    {True: 'Yes', False: 'No'}
)
summary['Serves_Elem']     = df['SCHOOL_ELEM'].map(
    {True: 'Yes', False: 'No'}
)
summary['Serves_Middle']   = df['SCHOOL_MIDDLE'].map(
    {True: 'Yes', False: 'No'}
)

# Gap rank per band — blank if not applicable
for band_code, band_label in BANDS.items():
    applicable_col = f'SCHOOL_{band_code}'
    gap_rank_col   = f'GAP_RANK_{band_code}'
    gap_tier_col   = f'GAP_TIER_{band_code}'
    ost_col        = f'OST_{band_code}_CNT'
    eec_col        = f'EEC_RAW_CNT_{band_code}'

    summary[f'Gap_Rank_{band_label}'] = df.apply(
        lambda r: int(r[gap_rank_col])
        if r[applicable_col] == True and pd.notna(r[gap_rank_col])
        else pd.NA,
        axis=1
    ).astype('Int64')

    summary[f'Gap_Tier_{band_label}'] = df.apply(
        lambda r: r[gap_tier_col]
        if r[applicable_col] == True
        else 'N/A',
        axis=1
    )

    summary[f'OST_Partners_{band_label}'] = df.apply(
        lambda r: int(r[ost_col])
        if r[applicable_col] == True
        else pd.NA,
        axis=1
    ).astype('Int64')

    summary[f'EEC_Programs_{band_label}'] = df.apply(
        lambda r: int(r[eec_col])
        if r[applicable_col] == True
        else pd.NA,
        axis=1
    ).astype('Int64')

# Primary gap band and tier
summary['Primary_Gap_Band'] = df['PRIMARY_GAP_BAND']
summary['Primary_Gap_Tier'] = df['PRIMARY_GAP_TIER']
summary['Primary_Gap_Label']= df['PRIMARY_GAP_LABEL']
summary['BPS_OI_Score']     = df['BPS_OI_SCORE'].round(3)

# Sort by worst applicable gap rank
# Use minimum gap rank across bands as sort key
# (rank 1 = most concerning — lowest number = highest priority)
def worst_rank(row):
    ranks = []
    for band_code in BANDS.keys():
        r = row.get(f'Gap_Rank_{BANDS[band_code]}')
        if pd.notna(r):
            ranks.append(int(r))
    return min(ranks) if ranks else 9999

summary['_sort_key'] = summary.apply(worst_rank, axis=1)
summary = summary.sort_values('_sort_key').drop(columns='_sort_key')

summary.to_csv('Rankings_Summary_All.csv', index=False)

print(f"\nSaved Rankings_Summary_All.csv — {len(summary)} schools")
print(f"\nTop 15 schools by worst applicable gap rank:")
display_cols = [
    'School_Name',
    'Gap_Rank_Pre-K',
    'Gap_Rank_Elementary',
    'Gap_Rank_Middle',
    'Primary_Gap_Band',
    'Primary_Gap_Tier',
    'OST_Partners_Total',
    'Zero_OST_Partners',
]
print(summary[display_cols].head(15).to_string(index=False))

# ==========================================
# SUMMARY STATISTICS
# ==========================================
print(f"\n{'='*50}")
print(f"DISTRICT SUMMARY")
print(f"{'='*50}")
print(f"Total BPS schools analyzed: {len(df)}")

for band_code, band_label in BANDS.items():
    applicable = (df[f'SCHOOL_{band_code}'] == True).sum()
    high_concern = (
        df[f'GAP_TIER_{band_code}'] == 'High Concern'
    ).sum()
    zero_eec = (df[f'ZERO_EEC_{band_code}'] == True).sum()
    print(f"\n{band_label}:")
    print(f"  Eligible schools:          {applicable}")
    print(f"  High Concern:              {high_concern}")
    print(f"  Zero EEC in isochrone:     {zero_eec}")

print(f"\nZero OST partners (any band): "
      f"{(df['ZERO_OST_ANY'] == True).sum()}")
print(f"High Concern (primary band):  "
      f"{(df['PRIMARY_GAP_TIER'] == 'High Concern').sum()}")
