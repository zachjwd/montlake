#!/usr/bin/env python3
"""
Sync documents tracker from Google Sheets to local CSV
"""

import subprocess
import sys
from datetime import datetime

# Google Sheets published CSV URL
SHEETS_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSP4O7viw6_OG70HMK7jVZTSYtG-uvoi0Q4Iyk_mvFnseTLqrf_Fdet_U9FX33e6ihkn9XLXuxEA2Bq/pub?output=csv"
LOCAL_CSV = "data/documents_tracker.csv"

print("📥 Syncing from Google Sheets...")
print()

try:
    # Download from Google Sheets using curl
    print(f"⬇️  Downloading from Google Sheets...")
    result = subprocess.run(
        ['curl', '-sL', SHEETS_URL, '-o', LOCAL_CSV],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise Exception(f"curl failed with code {result.returncode}: {result.stderr}")

    # Get line count
    with open(LOCAL_CSV, 'r') as f:
        lines = sum(1 for _ in f)

    print(f"✅ Synced successfully!")
    print(f"📊 {lines} rows downloaded")
    print(f"💾 Saved to: {LOCAL_CSV}")
    print(f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

except Exception as e:
    print(f"❌ Error syncing from Google Sheets:")
    print(f"   {str(e)}")
    print()
    sys.exit(1)
