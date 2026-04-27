import pandas as pd
import requests
import csv
import io
import time

# ==========================================
# CONFIGURATION
# ==========================================
INPUT_FILENAME  = "Current_Licensed_and_Funded_Early_Education_and_Care_Programs_20260307.csv"
OUTPUT_FILENAME = "EEC_Programs_Geocoded.csv"
UNMATCHED_LOG   = "EEC_Geocoding_Unmatched.csv"
BATCH_SIZE      = 1000

BOSTON_CITIES = [
    'Allston', 'Boston', 'Brighton', 'Charlestown', 'Dorchester',
    'East Boston', 'Hyde Park', 'Jamaica Plain', 'Mattapan',
    'Roslindale', 'Roxbury', 'South Boston', 'South End', 'West Roxbury'
]

RENAME_COLS = {
    'INFANT_TODDLER_BIRTH33MO': 'INFANTTODDLER_BIRTH33MO',
    'TODDLER_PRESCHOOL_15MOK':  'TODDLERPRESCHOOL_15MOK',
    'MULTI_AGEGROUP_BIRTH14YR': 'MULTIAGEGROUP_BIRTH14YR'
}

# Corrected street and zip for known problem records
# City is set to Boston for all records — zip disambiguates location
# Corrections documented in EEC_Geocoding_Unmatched.csv
ADDRESS_CORRECTIONS = {
    'P-169865': ('695 Truman Parkway',     '02136'),  # PARKWAY abbreviated in source
    'P-170124': ('25 Cummins Highway',     '02131'),  # No street name in source
    'P-170312': ('10 Causeway Street',     '02222'),  # Building name in source
    'P-170569': ('1 Financial Center',     '02111'),  # Building name in source
    'P-170827': ('821 Washington Street',  '02116'),  # Range address 821-831
    'P-173599': ('785 VFW Parkway',        '02132'),  # PKWY abbreviated in source
    'P-177133': ('150 Morrissey Boulevard','02125'),  # BLVD. abbreviated in source
    'P-177145': ('19 VFW Parkway',         '02132'),  # VFW PARKWAY abbreviated
    'P-247603': ('15 Egret Way',           '02126'),  # City field incorrect
    'P-249416': ('114 Western Avenue',     '02134'),  # City field incorrect
    'P-250388': ('23 Mount Ida Road',      '02122'),  # Typo: lda for Ida
    'P-257761': ('318 Tremont Street',     '02116'),  # Range address 318-342
    'P-259163': ('100 N Street',           '02127'),  # Neighborhood listed as city
    'P-268494': ('40 Smith Street',        '02120'),  # Neighborhood listed as city
}

# ==========================================
# LOAD AND PREPARE
# ==========================================
print(f"Loading {INPUT_FILENAME}...")
df = pd.read_csv(INPUT_FILENAME, encoding='latin1', dtype=str, low_memory=False)
print(f"  Loaded: {len(df)} records")

df = df.rename(columns=RENAME_COLS)

df['SNAPSHOT_DATE'] = pd.to_datetime(df['SNAPSHOT_DATE'], errors='coerce')
before = len(df)
df = df.sort_values('SNAPSHOT_DATE').groupby('PROVIDER_NUMBER').last().reset_index()
print(f"  After deduplication: {len(df)} records (dropped {before - len(df)} older snapshots)")

df = df[df['PROGRAM_CITY'].str.strip().isin(BOSTON_CITIES)].copy().reset_index(drop=True)
print(f"  After Boston area filter: {len(df)} records")

# Preserve original address for reference
df['FULL_ADDRESS'] = (
    df['PROGRAM_STREET_ADDRESS1'].str.strip() + ', ' +
    df['PROGRAM_CITY'].str.strip() + ', MA ' +
    df['PROGRAM_ZIPCODE'].str.strip()
)

# Build geocoding columns — apply corrections before geocoding
# so all records go through a single batch call
df['_GEO_STREET'] = df['PROGRAM_STREET_ADDRESS1'].str.strip()
df['_GEO_ZIP']    = df['PROGRAM_ZIPCODE'].str.strip()

corrections_applied = 0
for pid, (street, zipcode) in ADDRESS_CORRECTIONS.items():
    mask = df['PROVIDER_NUMBER'] == pid
    if mask.sum() > 0:
        df.loc[mask, '_GEO_STREET'] = street
        df.loc[mask, '_GEO_ZIP']    = zipcode
        corrections_applied += 1

print(f"  Address corrections applied: {corrections_applied}/{len(ADDRESS_CORRECTIONS)}")

# All records geocoded as Boston — zip code disambiguates neighborhood
df['_GEO_CITY'] = 'Boston'

# ==========================================
# BATCH GEOCODER
# ==========================================
def census_geocode_batch(batch_df):
    """
    Input columns: id, street, city, state, zip
    Returns: dict {id_str: (lat, lon)}
    """
    csv_content = batch_df.to_csv(index=False, header=False)
    url = "https://geocoding.geo.census.gov/geocoder/locations/addressbatch"
    try:
        r = requests.post(
            url,
            files={'addressFile': ('batch.csv', csv_content, 'text/csv')},
            data={'benchmark': 'Public_AR_Current'},
            timeout=120
        )
        r.raise_for_status()
    except requests.RequestException as e:
        print(f"    Batch request failed: {e}")
        return {}

    results = {}
    for row in csv.reader(io.StringIO(r.text)):
        if len(row) >= 6 and row[2].strip() == 'Match':
            try:
                lon_str, lat_str = row[5].strip().split(',')
                results[row[0].strip()] = (float(lat_str), float(lon_str))
            except (ValueError, IndexError):
                pass
    return results

geocode_input = pd.DataFrame({
    'id':     df.index.astype(str),
    'street': df['_GEO_STREET'],
    'city':   df['_GEO_CITY'],
    'state':  'MA',
    'zip':    df['_GEO_ZIP']
})

print(f"\nGeocoding {len(geocode_input)} records...")
all_results = {}
for i in range(0, len(geocode_input), BATCH_SIZE):
    batch     = geocode_input.iloc[i:i + BATCH_SIZE]
    batch_num = i // BATCH_SIZE + 1
    print(f"  Batch {batch_num} ({len(batch)} records)...", end=' ')
    results = census_geocode_batch(batch)
    all_results.update(results)
    print(f"{len(results)}/{len(batch)} matched")
    if i + BATCH_SIZE < len(geocode_input):
        time.sleep(2)

# ==========================================
# APPLY RESULTS AS FLOAT
# ==========================================
df['Latitude'] = pd.to_numeric(
    df.index.astype(str).map(lambda x: all_results.get(x, (None, None))[0]),
    errors='coerce'
)
df['Longitude'] = pd.to_numeric(
    df.index.astype(str).map(lambda x: all_results.get(x, (None, None))[1]),
    errors='coerce'
)

# Drop geocoding helper columns — not needed in output
df = df.drop(columns=['_GEO_STREET', '_GEO_CITY', '_GEO_ZIP'])

# ==========================================
# SUMMARY AND DOCUMENTATION
# ==========================================
total     = len(df)
matched   = df[['Latitude', 'Longitude']].notna().all(axis=1).sum()
unmatched = total - matched

print(f"\n{'='*50}")
print(f"Geocoding complete:")
print(f"  Total:     {total}")
print(f"  Matched:   {matched} ({matched/total*100:.1f}%)")
print(f"  Unmatched: {unmatched}")

if unmatched > 0:
    unmatched_df = df[df['Latitude'].isna()][
        ['PROVIDER_NUMBER', 'PROGRAM_NAME', 'FULL_ADDRESS', 'PROGRAM_TYPE']
    ].copy()
    unmatched_df['NOTE'] = 'Failed geocoding — excluded from spatial analysis'
    print(f"\nUnmatched records saved to {UNMATCHED_LOG}:")
    print(unmatched_df[['PROVIDER_NUMBER','PROGRAM_NAME','FULL_ADDRESS']].to_string())
    unmatched_df.to_csv(UNMATCHED_LOG, index=False)

df.to_csv(OUTPUT_FILENAME, index=False, encoding='utf-8-sig')
print(f"\nSaved to {OUTPUT_FILENAME}")