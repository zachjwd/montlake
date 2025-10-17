#!/usr/bin/env python3
"""
Update WSDOT Lead column based on section mapping
"""

import csv

# Section to WSDOT Lead mapping
section_leads = {
    '1-04': 'JV',
    '1-05': 'JV',
    '1-07': 'DH',
    '1-08': 'DH',
    '1-09': 'DH',
    '2.1': 'DH',
    '2.5': 'JV',
    '2.6': 'JV',
    '2.7': 'RB, JV',
    '2.8': 'SA',
    '2.9': 'RB',
    '2.10': 'RB, JV',
    '2.11': 'JV',
    '2.12': 'DH',
    '2.13': 'RB',
    '2.14': 'RB',
    '2.16': 'PA',
    '2.17': 'PA',
    '2.18': 'PA',
    '2.19': 'PA',
    '2.22': 'RB',
    '2.24': 'JV',
    '2.25': 'SS',
    '2.28': 'RB',
    '2.29': 'JV',
    '2.30': 'RB',
    '2.31': 'PA',
    '2.32': 'RB',
    '2.33': 'PA',
    '2.34': 'PA',
    '2.35': 'JV',
    '2.36': 'RB'
}

input_file = 'current_updated.csv'
output_file = 'current_updated.csv'

rows = []
updates = 0

# Read CSV
with open(input_file, 'r', encoding='latin-1') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames

    for row in reader:
        section_full = row.get('Section', '').strip()
        # Extract just the section number (e.g., "1-04" from "1-04 Scope of the Work")
        section = section_full.split()[0] if section_full else ''

        # Look up WSDOT Lead based on section
        if section in section_leads:
            old_lead = row.get('WSDOT Lead', '').strip()
            new_lead = section_leads[section]

            if old_lead != new_lead:
                row['WSDOT Lead'] = new_lead
                updates += 1
                print(f"Updated {row['Req ID']}: Section {section} -> {new_lead}")

        rows.append(row)

# Write updated CSV
with open(output_file, 'w', encoding='latin-1', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"\n✅ Updated {updates} rows with WSDOT Lead information")
print(f"📄 File saved: {output_file}")
