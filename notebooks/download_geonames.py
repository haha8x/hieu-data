#!/usr/bin/env python3
"""
Download GeoNames postal code data for any country

Usage:
    python download_geonames.py US
    python download_geonames.py CA
    python download_geonames.py VN
    
Available countries: https://download.geonames.org/export/zip/
"""

import sys
import urllib.request
import zipfile
from pathlib import Path

def download_geonames(country_code: str):
    """Download and extract GeoNames data for a country"""
    
    country_code = country_code.upper()
    script_dir = Path(__file__).parent.parent
    output_dir = script_dir / "data_geonames"
    output_dir.mkdir(exist_ok=True)
    
    url = f"https://download.geonames.org/export/zip/{country_code}.zip"
    zip_file = output_dir / f"{country_code}.zip"
    txt_file = output_dir / f"{country_code}.txt"
    
    print(f"🌍 Downloading GeoNames data for {country_code}...")
    print(f"   URL: {url}")
    
    try:
        # Download ZIP file
        print("   Downloading...")
        with urllib.request.urlopen(url, timeout=30) as response:
            zip_data = response.read()
        
        # Save ZIP
        with open(zip_file, 'wb') as f:
            f.write(zip_data)
        print(f"   ✅ Downloaded: {zip_file}")
        
        # Extract TXT
        print("   Extracting...")
        with zipfile.ZipFile(zip_file) as zf:
            zf.extract(f"{country_code}.txt", output_dir)
            # Also extract readme if exists
            if "readme.txt" in zf.namelist():
                zf.extract("readme.txt", output_dir / f"{country_code}_readme.txt")
        
        print(f"   ✅ Extracted: {txt_file}")
        
        # Show stats
        import pandas as pd
        df = pd.read_csv(txt_file, sep='\t', header=None, usecols=[1, 2])
        print(f"\n✨ Success! {len(df):,} postal codes downloaded for {country_code}")
        print(f"📁 Files saved to: {output_dir}")
        
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"\n❌ Error: Country code '{country_code}' not found")
            print(f"   Check available countries at:")
            print(f"   https://download.geonames.org/export/zip/")
        else:
            print(f"\n❌ HTTP Error: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python download_geonames.py <COUNTRY_CODE>")
        print("\nExamples:")
        print("  python download_geonames.py US  # United States")
        print("  python download_geonames.py CA  # Canada")
        print("  python download_geonames.py GB  # United Kingdom")
        print("  python download_geonames.py DE  # Germany")
        print("  python download_geonames.py VN  # Vietnam")
        print("\nAvailable countries:")
        print("  https://download.geonames.org/export/zip/")
        sys.exit(1)
    
    country = sys.argv[1]
    download_geonames(country)
