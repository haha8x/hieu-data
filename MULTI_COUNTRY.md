# 🌍 Multi-Country Support Guide

This project now supports postal code lookups for **any country** available on GeoNames!

## 🗺️ Available Countries

GeoNames provides postal code data for 250+ countries. Popular ones include:

| Country | Code | Postal Codes |
|---------|------|--------------|
| 🇺🇸 United States | US | 41,487 |
| 🇨🇦 Canada | CA | 1,657 |
| 🇬🇧 United Kingdom | GB | ~1.7M |
| 🇩🇪 Germany | DE | ~16K |
| 🇫🇷 France | FR | ~37K |
| 🇯🇵 Japan | JP | ~124K |
| 🇦🇺 Australia | AU | ~17K |
| 🇮🇹 Italy | IT | ~18K |
| 🇪🇸 Spain | ES | ~14K |
| 🇧🇷 Brazil | BR | ~5.5K |
| 🇲🇽 Mexico | MX | ~145K |

**Full list:** https://download.geonames.org/export/zip/

## 🔧 How to Use

### Option 1: Change Country in Main Script

Edit `notebooks/01_combine_liheap_data.py`:

```python
# Line 20: Change country code
GEONAMES_COUNTRY = "CA"  # Canada
# or
GEONAMES_COUNTRY = "GB"  # United Kingdom
# or
GEONAMES_COUNTRY = "DE"  # Germany
```

Then run normally:
```bash
python notebooks/01_combine_liheap_data.py
```

### Option 2: Download Data for Multiple Countries

Use the helper script to download data for any country:

```bash
# Download Canada postal codes
python notebooks/download_geonames.py CA

# Download UK postal codes  
python notebooks/download_geonames.py GB

# Download Germany postal codes
python notebooks/download_geonames.py DE
```

The script will:
- ✅ Download latest data from GeoNames
- ✅ Extract and save to `data_geonames/`
- ✅ Show statistics (number of postal codes)

### Option 3: Manually Download

1. Visit: https://download.geonames.org/export/zip/
2. Download the ZIP file for your country (e.g., `CA.zip`)
3. Extract `CA.txt` to `data_geonames/` folder
4. Update `GEONAMES_COUNTRY = "CA"` in the script

## 📋 Example: Using Canada Data

```python
# 1. Download Canada data
$ python notebooks/download_geonames.py CA
# Output: ✨ Success! 1,657 postal codes downloaded for CA

# 2. Update script
# Edit line 20 in 01_combine_liheap_data.py:
GEONAMES_COUNTRY = "CA"

# 3. Run script
$ python notebooks/01_combine_liheap_data.py
# Output: ✅ Loaded 1657 ZIP codes from HTTP (latest data)
```

## 🔄 How It Works

The script uses a **smart loading strategy**:

1. **Try HTTP first** (latest data for specified country)
   ```
   https://download.geonames.org/export/zip/{COUNTRY}.zip
   ```

2. **Fallback to local** (if HTTP fails)
   ```
   data_geonames/{COUNTRY}.txt
   ```

3. **Graceful degradation** (if both fail)
   - Continues with internal ZIP→City mapping
   - No crash, just warning

## 📝 Notes

- **Not all countries have data** - Check the GeoNames website first
- **Postal code formats vary** by country:
  - US: 5 digits (12345)
  - Canada: 6 chars (A1B 2C3)
  - UK: Variable (SW1A 1AA)
- The script automatically handles different formats
- Data is updated regularly on GeoNames

## 🧪 Testing Different Countries

```bash
# Test with US (default)
GEONAMES_COUNTRY="US" python notebooks/01_combine_liheap_data.py

# Test with Canada
GEONAMES_COUNTRY="CA" python notebooks/01_combine_liheap_data.py

# Test with UK
GEONAMES_COUNTRY="GB" python notebooks/01_combine_liheap_data.py
```

## ⚙️ Technical Details

The country code is used in:
- HTTP download URL: `https://download.geonames.org/export/zip/{COUNTRY}.zip`
- Local file path: `data_geonames/{COUNTRY}.txt`
- ZIP file extraction: `{COUNTRY}.txt` from archive

All postal code mappings are built dynamically from the selected country's data!
