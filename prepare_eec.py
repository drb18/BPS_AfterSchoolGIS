import pandas as pd

INPUT_FILENAME = "EEC_Programs_Geocoded.csv"

df = pd.read_csv(INPUT_FILENAME, encoding='utf-8-sig', low_memory=False)

# Drop unmatched records
before = len(df)
df = df.dropna(subset=['Latitude', 'Longitude'])
print(f"Dropped {before - len(df)} records missing coordinates")

# ==========================================
# SPLIT FCC BEFORE BAND ASSIGNMENT
# FCC programs do not report age-group breakdowns
# Assumed to serve birth-13 by Massachusetts licensing default
# ==========================================
fcc = df[df['PROGRAM_TYPE'] == 'Family Child Care'].copy()
ctr = df[df['PROGRAM_TYPE'] != 'Family Child Care'].copy()

print(f"\nFamily Child Care programs: {len(fcc)}")
print(f"Center-based and other programs: {len(ctr)}")

# ==========================================
# GRADE BAND FLAGS — CENTER-BASED ONLY
# ==========================================
prek_cols  = ['PRESCHOOL_33MOK', 'TODDLERPRESCHOOL_15MOK',
              'PRESCHOOLSA_33MO8YR', 'MULTIAGEGROUP_BIRTH14YR']
elem_cols  = ['KINDERGARTEN', 'KINDERGARTEN_SCHOOLAGE',
              'SCHOOLAGE_5YR14YR', 'PRESCHOOLSA_33MO8YR',
              'MULTIAGEGROUP_BIRTH14YR']
middle_cols = ['SCHOOLAGE_5YR14YR', 'MULTIAGEGROUP_BIRTH14YR']

def serves_band(row, cols):
    for c in cols:
        val = row.get(c)
        if pd.notna(val) and str(val).strip() not in ('', '0'):
            return True
    return False

ctr['SERVES_PREK']   = ctr.apply(lambda r: serves_band(r, prek_cols),   axis=1)
ctr['SERVES_ELEM']   = ctr.apply(lambda r: serves_band(r, elem_cols),   axis=1)
ctr['SERVES_MIDDLE'] = ctr.apply(lambda r: serves_band(r, middle_cols), axis=1)

# Keep only programs serving at least one band
ctr_filtered = ctr[ctr['SERVES_PREK'] | ctr['SERVES_ELEM'] | ctr['SERVES_MIDDLE']].copy()

print(f"\nCenter-based programs serving at least one band: {len(ctr_filtered)}")
print(f"  Pre-K:       {ctr_filtered['SERVES_PREK'].sum()}")
print(f"  Elementary:  {ctr_filtered['SERVES_ELEM'].sum()}")
print(f"  Middle:      {ctr_filtered['SERVES_MIDDLE'].sum()}")

# ==========================================
# QUALITY FLAGS — APPLIED TO BOTH OUTPUTS
# Licensed = meets state minimum
# VOUCHER_CONTRACT = accepts subsidies (family access)
# C3_ATTESTATION = higher quality certification
# ==========================================
for dataset in [ctr_filtered, fcc]:
    dataset['QUALITY_LICENSED'] = (
        dataset['LICENSED_PROVIDER_STATUS'].str.strip().str.lower() == 'current'
    )
    dataset['QUALITY_VOUCHER'] = (
        dataset['VOUCHER_CONTRACT'].astype(str).str.strip().str.lower() == 'true'
    )
    dataset['QUALITY_C3'] = (
        dataset['C3_ATTESTATION'].astype(str).str.strip().str.lower() == 'yes'
    )

# ==========================================
# FCC SUMMARY
# ==========================================
print(f"\nFamily Child Care summary:")
print(f"  With valid coordinates:  {len(fcc)}")
print(f"  Current license:         {fcc['QUALITY_LICENSED'].sum()}")
print(f"  Voucher/contract:        {fcc['QUALITY_VOUCHER'].sum()}")
print(f"  C3 attestation:          {fcc['QUALITY_C3'].sum()}")

# ==========================================
# SAVE
# ==========================================
ctr_filtered.to_csv('EEC_Center_Clean.csv', index=False)
fcc.to_csv('EEC_FCC_Clean.csv', index=False)

print(f"\nSaved:")
print(f"  EEC_Center_Clean.csv — {len(ctr_filtered)} records")
print(f"  EEC_FCC_Clean.csv    — {len(fcc)} records")