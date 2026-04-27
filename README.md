# BPS Out-of-School Time Gap Analysis

GIS product and data pipeline for the Boston Public Schools OST Gap Map.
The live map is hosted at **https://drb18.github.io/BPS_AfterSchoolGIS/**.
Full methodology is documented in the Data Appendix.

---

## Requirements

**Python 3.11**

| Package | Version | Purpose |
|---|---|---|
| pandas | 3.0.0 | Data loading and transformation |
| geopandas | 1.1.2 | Spatial joins and GeoPackage I/O |
| shapely | 2.1.2 | Geometry operations (geopandas dependency) |
| pyproj | 3.7.2 | CRS handling (geopandas dependency) |
| pyogrio | 0.12.1 | GeoPackage read/write backend |
| numpy | 2.4.2 | Numeric operations |
| requests | 2.32.5 | Census Geocoder batch API calls |
| openpyxl | 3.1.5 | Reading BPS Partner Programs Excel file |
| scipy | 1.17.1 | Statistical utilities |

Install all dependencies into a virtual environment:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install pandas==3.0.0 geopandas==1.1.2 numpy==2.4.2 requests==2.32.5 openpyxl==3.1.5 scipy==1.17.1
```

Geopandas will pull in shapely, pyproj, and pyogrio automatically.

---

## Source Data

Two large source files are not included in this repository and must be downloaded before running the pipeline.

**Massachusetts Student Enrollment by Grade, Race/Ethnicity, Gender, and Selected Populations**
Download from the Massachusetts Education to Career data portal (DESE). Filter to district code `00350000` (Boston Public Schools), school year 2026. Save as:
`Enrollment__Grade,_Race_Ethnicity,_Gender,_and_Selected_Populations_20260306.csv`

**Opportunity Insights Neighborhood Outcomes by Census Tract**
Download from the Opportunity Insights data page (Harvard University). The full national file is approximately 2.5 GB. Save as `tract_outcomes_early.csv`, then run `tract_outcomes_filter_full.py` to produce `suffolk_filtered.csv`, which is the file actually used in the pipeline. `suffolk_filtered.csv` is included in this repository so this step only needs to be repeated if refreshing the Opportunity Insights data.

All other source files are included in this repository at their original filenames.

---

## Pipeline Execution Order

Run scripts in the following order. All scripts read from and write to the project root directory.

```
1. geocode_eec_v2.py
   Reads:  Current_Licensed_and_Funded_Early_Education_and_Care_Programs_20260307.csv
   Writes: EEC_Programs_Geocoded.csv, EEC_Geocoding_Unmatched.csv

2. prepare_eec.py
   Reads:  EEC_Programs_Geocoded.csv
   Writes: EEC_Center_Clean.csv, EEC_FCC_Clean.csv

3. prepare_schools.py
   Reads:  SCHOOLS_PT.shp, Enrollment CSV (see Source Data), OI Scores CSV, name_crosswalk.csv
   Writes: BPS_Schools.gpkg

4. prepare_partners.py
   Reads:  BPS Partner Programs.xlsx, BPS_Schools.gpkg
   Writes: Partners_OST.csv, Partners_All.csv, Partners_OST_Summary.csv

   — Generate walking isochrones in QGIS using ORS Tools plugin before step 5 —
   — Output: BPS_Isochrones.gpkg (included in repository) —

5. compute_gaps.py
   Reads:  BPS_Schools.gpkg, BPS_Isochrones.gpkg, EEC_Center_Clean.csv, Partners_OST_Summary.csv
   Writes: BPS_Schools_Ranked.gpkg, Rankings_PREK.csv, Rankings_ELEM.csv, Rankings_MIDDLE.csv

6. add_symbology_to_schools.py
   Reads:  BPS_Schools_Ranked.gpkg, EEC_Center_Clean.csv
   Writes: BPS_Schools_Ranked.gpkg (updated), EEC_Center_Clean.csv (updated)

7. add_voucher_EEC.py
   Reads:  EEC_FCC_Clean.csv
   Writes: EEC_FCC_Clean.csv (updated with QUALITY_LABEL field)

8. ranking_summary.py
   Reads:  BPS_Schools_Ranked.gpkg
   Writes: Rankings_Summary_PREK.csv, Rankings_Summary_ELEM.csv,
           Rankings_Summary_MIDDLE.csv, Rankings_Summary_All.csv

   — Export web map from QGIS using qgis2web plugin before step 9 —
   — Output directory: BPS_Gap_Map_Web/ —

9. post_process_web_export.py
   Reads:  BPS_Gap_Map_Web/ (qgis2web export)
   Writes: BPS_Gap_Map_Web/ (modified in place)
```

---

## Isochrone Generation

Walking isochrones are generated in QGIS 3.x using the **ORS Tools plugin** with a free OpenRouteService API key.

Settings used:
- Travel mode: foot-walking
- Time interval: 10 minutes
- Input layer: BPS_Schools.gpkg (all 105 school points)

Export the result as `BPS_Isochrones.gpkg`. The generated file is included in this repository so this step only needs to be repeated if schools change.

---

## Web Export

The map is exported from QGIS using the **qgis2web plugin** with the OpenLayers exporter. Export to `BPS_Gap_Map_Web/`. After export, run `post_process_web_export.py` to apply custom popups, legend, search bar, grade band filters, and analytics drawer.

The script is idempotent — re-running it on an already-processed export will not duplicate injected content.

---

## Repository Contents

| File / Folder | Description |
|---|---|
| `geocode_eec_v2.py` | Geocodes EEC programs via Census batch API |
| `prepare_eec.py` | Cleans and splits EEC programs by type and band |
| `prepare_schools.py` | Joins enrollment and OI scores to school points |
| `prepare_partners.py` | Categorizes and joins BPS partner programs |
| `compute_gaps.py` | Computes gap rankings by school and grade band |
| `add_symbology_to_schools.py` | Adds precomputed display fields for QGIS/qgis2web |
| `add_symbology_to_EEC.py` | Earlier standalone version (add_symbology_to_schools.py supersedes) |
| `add_voucher_EEC.py` | Adds QUALITY_LABEL field to FCC program file |
| `ranking_summary.py` | Produces formatted ranking CSVs from GeoPackage |
| `post_process_web_export.py` | Post-processes qgis2web HTML/JS export |
| `tract_outcomes_filter_full.py` | Filters Opportunity Insights national file to Suffolk County |
| `name_crosswalk.csv` | Manual school name crosswalk (11 records) |
| `manual_geocode_corrections.csv` | Address corrections applied before geocoding (14 records) |
| `BPS_Gap_Map_Web/` | Web map deliverable (self-contained, opens in any browser) |
