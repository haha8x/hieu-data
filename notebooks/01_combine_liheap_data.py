import pandas as pd
from pathlib import Path
import re
import numpy as np

# Set random seed for reproducibility
np.random.seed(42)
import random
random.seed(42)

# ========== 1. PATH CONFIGURATION (EDIT THIS) ==========

# Use relative paths from script location
script_dir = Path(__file__).parent.parent
data_folder = script_dir / "Data_raw_SDGE LIHEAP"
combined_output = script_dir / "data_clean" / "combined_raw_liheap_2023_2025.xlsx"
final_output = script_dir / "data_clean" / "liheap_clean_2023_2025.xlsx"

# ========== 2. HELPER FUNCTIONS ==========

def detect_header_row(file_path: Path, max_rows: int = 10) -> int:
    tmp = pd.read_excel(file_path, header=None, nrows=max_rows)

    for i in range(min(max_rows, len(tmp))):
        row = tmp.iloc[i].astype(str)
        has_alpha = row.str.contains(r"[A-Za-z]", regex=True).sum()
        non_null = row.notna().sum()
        if non_null >= 3 and has_alpha >= 2:
            return i
    return 0


COLUMN_MAPPING = {
    # City
    "CV_EnergyAssistance[City(Service Address)]": "City",
    "Service City": "City",
    "City": "City",

    # Zip / Postal Code
    "CV_EnergyAssistance[Post Code (Service Address)]": "Zip_Code",
    "CV_EnergyAssistance[Zipcode (Business Partner Address)]": "Zip_Code",
    "Zipcode (Business Partner Address)": "Zip_Code",
    "Zip Code": "Zip_Code",
    "ZIP": "Zip_Code",
    "Zip_Code": "Zip_Code",

    # Date (Created On)
    "CV_EnergyAssistance[created On (Pledge Details)]": "Created_On",
    "CV_EnergyAssistance[Created On (Pledge Details)]": "Created_On",
    "CV_EnergyAssistance[Created on (MM/DD/YYYY)]": "Created_On",
    "CV_EnergyAssistance[Created On (PL)]": "Created_On",
    "Created_On": "Created_On",
    "Created On": "Created_On",

    # Pledge Amount
    "[Pledge_Amount]": "Pledge_Amount",
    "Pledge Amount": "Pledge_Amount",
    "Pledge_Amount": "Pledge_Amount",
    "CV_EnergyAssistance[Pledge Amount]": "Pledge_Amount",
}

REQUIRED_STRICT = ["Zip_Code", "Created_On", "Pledge_Amount"]
OPTIONAL_COLS = ["City"]

# ========== 3. LOAD + NORMALIZE EACH FILE ==========

# Sort files by name to ensure consistent order across systems
excel_files = sorted(data_folder.rglob("*.xls*"), key=lambda x: x.name)

print(f"Number of Excel files found: {len(excel_files)}")
print("Sample files:", [f.name for f in excel_files[:5]])

if not excel_files:
    raise FileNotFoundError(f"No Excel files (.xls or .xlsx) found under: {data_folder}")

normalized_dfs = []
skipped_files = []

for file in excel_files:
    print(f"\nProcessing file: {file.name}")

    header_row = detect_header_row(file)
    print(f"  Detected header row: {header_row}")

    df = pd.read_excel(file, header=header_row)

    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
    )

    df = df.rename(columns=lambda c: COLUMN_MAPPING.get(c, c))

    print("  Columns after rename:", df.columns.tolist())

    missing_required = [c for c in REQUIRED_STRICT if c not in df.columns]
    if missing_required:
        print(f"  Skipping file (missing required columns): {missing_required}")
        skipped_files.append((file.name, missing_required))
        continue

    for col in OPTIONAL_COLS:
        if col not in df.columns:
            df[col] = pd.NA

    keep_cols = ["City", "Zip_Code", "Created_On", "Pledge_Amount"]
    df = df[keep_cols].copy()
    df["SourceFile"] = file.name

    normalized_dfs.append(df)

if not normalized_dfs:
    raise RuntimeError("No valid files after normalization. Check mappings and required columns.")

# ========== 4. COMBINE ALL NORMALIZED DATAFRAMES ==========

df_all = pd.concat(normalized_dfs, ignore_index=True)
print("\nCombined df_all shape:", df_all.shape)
print(df_all.head())

combined_output.parent.mkdir(parents=True, exist_ok=True)
df_all.to_excel(combined_output, index=False)
print(f"Combined normalized file saved to: {combined_output}")

# ========== 5. CLEAN ZIP / DATE / PLEDGE AMOUNT ==========

df_all["Zip_Code"] = (
    df_all["Zip_Code"]
        .astype(str)
        .str.replace(r"\.0$", "", regex=True)
        .str.extract(r"(\d{5})", expand=False)
        .str.zfill(5)
)

def parse_date(x):
    if pd.isna(x):
        return pd.NaT
    if isinstance(x, (int, float)):
        try:
            return pd.to_datetime(str(int(x)), format="%Y%m%d")
        except Exception:
            return pd.NaT
    return pd.to_datetime(x, errors="coerce")

df_all["Created_On"] = df_all["Created_On"].apply(parse_date)

df_all["YearMo"] = df_all["Created_On"].dt.to_period("M").astype(str)

df_all["Pledge_Amount"] = (
    df_all["Pledge_Amount"]
        .astype(str)
        .str.replace(r"[^0-9\.\-]", "", regex=True)
)
df_all["Pledge_Amount"] = pd.to_numeric(df_all["Pledge_Amount"], errors="coerce")

# ========== 6. BUILD ZIP → CITY FROM EXISTING DATA ==========

city_series = df_all["City"].astype(str)
missing_city_mask = (
    df_all["City"].isna() |
    city_series.str.strip().eq("") |
    city_series.str.strip().str.upper().eq("NAN")
)

print(f"Rows with missing City BEFORE fill: {missing_city_mask.sum()}")

valid_city_mask = ~missing_city_mask

# Use deterministic aggregation for ZIP→CITY mapping
# Sort before taking the most common value to ensure consistency
zip_city_map = (
    df_all.loc[valid_city_mask, ["Zip_Code", "City"]]
        .assign(City=lambda d: d["City"].astype(str).str.strip().str.upper())
        .dropna()
        .groupby("Zip_Code")["City"]
        .agg(lambda s: s.value_counts().sort_index().idxmax())  # sort_index() ensures deterministic order
        .to_dict()
)

print(f"ZIP→CITY mapping size (from existing data): {len(zip_city_map)}")

# Fill từ chính data LIHEAP trước
df_all.loc[missing_city_mask, "City"] = (
    df_all.loc[missing_city_mask, "Zip_Code"].map(zip_city_map)
)

# ========== 7. DÙNG PGEOCODE CHO NHỮNG DÒNG VẪN THIẾU CITY ==========

# mask sau khi fill lần 1
city_series2 = df_all["City"].astype(str)
still_missing_mask = (
    df_all["City"].isna() |
    city_series2.str.strip().eq("") |
    city_series2.str.strip().str.upper().eq("NAN")
)

print(f"Rows with missing City AFTER internal mapping: {still_missing_mask.sum()}")

# Strategy: Try HTTP first (latest data), fallback to local if fails
geonames_zip_city = {}
geonames_file = script_dir / "data_geonames" / "US.txt"

# Try loading from HTTP first (latest data)
print("Attempting to load GeoNames data from HTTP...")
try:
    import urllib.request
    import zipfile
    import io
    
    # Download and extract in memory
    url = "https://download.geonames.org/export/zip/US.zip"
    print(f"Downloading from {url}...")
    
    with urllib.request.urlopen(url, timeout=10) as response:
        zip_data = response.read()
    
    # Extract US.txt from zip
    with zipfile.ZipFile(io.BytesIO(zip_data)) as zf:
        with zf.open("US.txt") as txt_file:
            df_geo = pd.read_csv(
                txt_file,
                sep="\t",
                header=None,
                names=["country", "postal_code", "place_name", "admin_name1", "admin_code1",
                       "admin_name2", "admin_code2", "admin_name3", "admin_code3",
                       "latitude", "longitude", "accuracy"],
                dtype={"postal_code": str},
                usecols=["postal_code", "place_name"]
            )
            # Create ZIP → City mapping
            geonames_zip_city = (
                df_geo.dropna(subset=["postal_code", "place_name"])
                .groupby("postal_code")["place_name"]
                .first()
                .str.upper()
                .to_dict()
            )
    print(f"✅ Loaded {len(geonames_zip_city)} ZIP codes from HTTP (latest data)")

except Exception as e:
    print(f"⚠️ HTTP failed: {e}")
    print("Falling back to local GeoNames data...")
    
    # Fallback to local file
    if geonames_file.exists():
        try:
            df_geo = pd.read_csv(
                geonames_file,
                sep="\t",
                header=None,
                names=["country", "postal_code", "place_name", "admin_name1", "admin_code1",
                       "admin_name2", "admin_code2", "admin_name3", "admin_code3",
                       "latitude", "longitude", "accuracy"],
                dtype={"postal_code": str},
                usecols=["postal_code", "place_name"]
            )
            geonames_zip_city = (
                df_geo.dropna(subset=["postal_code", "place_name"])
                .groupby("postal_code")["place_name"]
                .first()
                .str.upper()
                .to_dict()
            )
            print(f"✅ Loaded {len(geonames_zip_city)} ZIP codes from local file")
        except Exception as e2:
            print(f"❌ Local file also failed: {e2}")
    else:
        print(f"❌ Local file not found at {geonames_file}")

def lookup_city(zip_code: str):
    if pd.isna(zip_code):
        return None
    # Clean ZIP code (pad to 5 digits)
    zip_clean = str(zip_code).zfill(5)
    return geonames_zip_city.get(zip_clean)

if geonames_zip_city:
    df_all.loc[still_missing_mask, "City"] = (
        df_all.loc[still_missing_mask, "Zip_Code"].apply(lookup_city)
    )
else:
    print("⚠️ No GeoNames data available - skipping city lookup")

print(f"Rows with missing City AFTER GeoNames lookup: {df_all['City'].isna().sum()}")

df_all["City"] = df_all["City"].astype(str).str.strip().str.upper()

# ========== 8. FILTER DATE RANGE ==========

start_date = "2023-01"
end_date = "2025-06"

df_all = df_all[
    (df_all["YearMo"] >= start_date) &
    (df_all["YearMo"] <= end_date)
].copy()

print(f"\nAfter filtering {start_date} to {end_date}: {df_all.shape[0]} rows")

# ========== 9. FINAL DATASET ==========

df_final = df_all[["City", "Zip_Code", "YearMo", "Pledge_Amount"]].copy()
df_final["Zip_Code"] = df_final["Zip_Code"].astype(str)

print("\nFinal df_final shape:", df_final.shape)
print(df_final.head())

# ========== 10. SAVE FINAL CLEAN DATASET ==========

final_output.parent.mkdir(parents=True, exist_ok=True)

with pd.ExcelWriter(final_output, engine="openpyxl") as writer:
    df_final.to_excel(writer, index=False, sheet_name="LIHEAP_Data")
    worksheet = writer.sheets["LIHEAP_Data"]
    for row in range(2, len(df_final) + 2):
        cell = worksheet.cell(row=row, column=2)  # Zip_Code
        cell.number_format = "@"

print(f"\nFinal cleaned file saved to: {final_output}")

if skipped_files:
    print("\nSkipped files (missing required columns):")
    for fname, cols in skipped_files:
        print(f"  {fname}: {cols}")