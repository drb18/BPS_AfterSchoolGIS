import pandas as pd
import geopandas as gpd
import numpy as np

# ==========================================
# SCHOOLS — Precomputed display fields
# ==========================================
schools = gpd.read_file('BPS_Schools_Ranked.gpkg')

# SIZE_CAT: enrollment in primary gap band
# binned into 4 categories for fixed symbol sizes
# qgis2web can render fixed sizes per category
def enrollment_size_cat(row):
    band = row.get('PRIMARY_GAP_BAND')
    if band == 'Not applicable' or pd.isna(band):
        return 'XS'
    enr_col = {
        'PREK':   'ENR_PREK',
        'ELEM':   'ENR_ELEM',
        'MIDDLE': 'ENR_MIDDLE'
    }.get(band)
    if enr_col is None:
        return 'XS'
    enr = row.get(enr_col, 0)
    if pd.isna(enr) or enr == 0:
        return 'XS'
    if enr < 100:
        return 'S'
    if enr < 300:
        return 'M'
    if enr < 600:
        return 'L'
    return 'XL'

schools['SIZE_CAT'] = schools.apply(enrollment_size_cat, axis=1)

# SYMBOL_TYPE: combines gap tier and zero OST flag
# Used as single categorized field for qgis2web
# Format: "High Concern - No Partners" or "High Concern"
def symbol_type(row):
    tier     = row.get('PRIMARY_GAP_TIER', 'Not applicable')
    zero_ost = row.get('ZERO_OST_ANY', False)
    if tier == 'Not applicable':
        return 'Not applicable'
    if zero_ost:
        return f"{tier} — No Partners"
    return tier

schools['SYMBOL_TYPE'] = schools.apply(symbol_type, axis=1)

print("SIZE_CAT distribution:")
print(schools['SIZE_CAT'].value_counts().to_string())
print("\nSYMBOL_TYPE distribution:")
print(schools['SYMBOL_TYPE'].value_counts().to_string())

# ==========================================
# EEC CENTERS — Precomputed display fields
# ==========================================
eec = pd.read_csv('EEC_Center_Clean.csv',
                  encoding='utf-8-sig', low_memory=False)

# BAND_LABEL: single readable field for categorized renderer
def band_label(row):
    prek   = row.get('SERVES_PREK',   False)
    elem   = row.get('SERVES_ELEM',   False)
    middle = row.get('SERVES_MIDDLE', False)
    count  = sum([bool(prek), bool(elem), bool(middle)])
    if count > 1:
        return 'Multiple Bands'
    if prek:
        return 'Pre-K only'
    if elem:
        return 'Elementary only'
    if middle:
        return 'Middle only'
    return 'Unknown'

eec['BAND_LABEL'] = eec.apply(band_label, axis=1)

# CAP_CAT: capacity binned for fixed symbol sizes
def cap_size_cat(cap):
    if pd.isna(cap) or cap == 0:
        return 'S'
    if cap < 40:
        return 'S'
    if cap < 80:
        return 'M'
    if cap < 150:
        return 'L'
    return 'XL'

eec['CAP_CAT'] = eec['LICENSED_CAPACITY'].apply(cap_size_cat)

print("\nBAND_LABEL distribution:")
print(eec['BAND_LABEL'].value_counts().to_string())
print("\nCAP_CAT distribution:")
print(eec['CAP_CAT'].value_counts().to_string())

# ==========================================
# SAVE
# ==========================================
schools.to_file('BPS_Schools_Ranked.gpkg', driver='GPKG')
print(f"\nSaved BPS_Schools_Ranked.gpkg with display fields")

eec.to_csv('EEC_Center_Clean.csv', index=False, encoding='utf-8-sig')
print(f"Saved EEC_Center_Clean.csv with display fields")
