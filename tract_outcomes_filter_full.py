import pandas as pd

input_file = "tract_outcomes_early.csv"
output_file = "suffolk_filtered.csv"

# --- Step 1: Read header only ---
df_header = pd.read_csv(input_file, nrows=0)

# --- Step 2: Determine which columns to keep ---
base_cols = list(df_header.columns[:3])  # first 3 columns
kfr_cols = [c for c in df_header.columns if c.startswith("kfr_pooled_pooled_p25")]

cols_to_keep = base_cols + kfr_cols

# Ensure county column is included for filtering even if not in cols_to_keep
if "county" not in cols_to_keep:
    cols_to_keep.append("county")

# --- Step 3: Stream through the file in chunks ---
chunksize = 20000  # safe for large files

first_write = True

for chunk in pd.read_csv(input_file, usecols=cols_to_keep, chunksize=chunksize):
    # Filter to Suffolk County (FIPS 025)
    filtered = chunk[(chunk["state"] == 25) & (chunk["county"] == 25)]

    if filtered.empty:
        continue

    # Write header only once
    filtered.to_csv(output_file, mode="w" if first_write else "a",
                    index=False, header=first_write)
    first_write = False

print(f"Finished filtering. Output written to {output_file}")