#!/usr/bin/env python3
"""
Create FINAL complete contract documents review tracker
Includes ALL change orders (001-189) and DB's Proposal
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
import csv

print("📊 Creating FINAL Complete Contract Documents Review Tracker...")
print()

# Load existing appendices inventory
appendices_df = pd.read_csv('/Users/z/Desktop/git/montlake-closeout/appendices_inventory.csv')
print(f"✅ Loaded {len(appendices_df)} appendices")

# Load change orders inventory
co_df = pd.read_csv('/Users/z/Desktop/git/montlake-closeout/all_change_orders_inventory.csv')
print(f"✅ Loaded {len(co_df)} change orders")
print()

# Build complete contract documents list
all_docs = []

# ==============================================================================
# 1. CHANGE ORDERS (001-189)
# ==============================================================================

for _, co in co_df.iterrows():
    co_num = co['CO_Number']

    # Determine priority based on CO number
    if int(co_num) >= 166:
        priority = 'CRITICAL'  # Recent COs most likely to affect closeout
    elif int(co_num) >= 100:
        priority = 'HIGH'
    elif int(co_num) >= 50:
        priority = 'MEDIUM'
    else:
        priority = 'LOW'

    # Handle missing/no-PDF cases
    if co['Status'] == 'MISSING':
        notes = f"CO {co_num} - No folder found for this CO number"
        filename = f"CO {co_num} - MISSING"
    elif 'NO EXECUTED PDF' in co['Status']:
        notes = f"CO {co_num} - Folder exists but no signed/executed PDF found"
        filename = f"CO {co_num} - {co['Folder']}"
    else:
        notes = ''
        filename = co['Filename']

    all_docs.append({
        'Category': '1 - Change Orders',
        'Appendix_Number': f"CO {co_num}",
        'Subfolder': co['Folder'],
        'Filename': filename,
        'File_Type': '.PDF' if co['Status'] == 'EXECUTED' else 'MISSING',
        'Size_MB': co['Size_MB'],
        'Modified_Date': co['Modified_Date'],
        'Full_Path': co['Full_Path'],
        'Priority': priority,
        'Notes': notes
    })

print(f"✅ Added {len(co_df)} change orders to tracker")

# ==============================================================================
# 2. CONTRACT FORM (Executed)
# ==============================================================================

contract_form_path = Path("/Users/z/Library/CloudStorage/OneDrive-WashingtonStateDepartmentofTransportation/TheBRIDGE - Montlake - Contract Documents/Design-Build Contract/Executed Contract Form.pdf")
if contract_form_path.exists():
    all_docs.append({
        'Category': '2 - Contract Form',
        'Appendix_Number': '',
        'Subfolder': '',
        'Filename': 'Executed Contract Form.pdf',
        'File_Type': '.PDF',
        'Size_MB': f"{contract_form_path.stat().st_size / (1024*1024):.2f}",
        'Modified_Date': datetime.fromtimestamp(contract_form_path.stat().st_mtime).strftime('%Y-%m-%d'),
        'Full_Path': str(contract_form_path),
        'Priority': 'CRITICAL',
        'Notes': 'May contain Exhibit B (WSDOT-Identified Betterments)'
    })

print(f"✅ Added Contract Form")

# ==============================================================================
# 3. EXHIBIT B - Within DB's Proposal
# ==============================================================================

# Note: Exhibit B is within the DB's Proposal, we'll note this

# ==============================================================================
# 4. GENERAL PROVISIONS (Chapter 1)
# ==============================================================================

chapter1_path = Path("/Users/z/Library/CloudStorage/OneDrive-WashingtonStateDepartmentofTransportation/TheBRIDGE - Montlake - Change Management  Documents/120_RFP Conformed to COs/Chapter 1.docx")
if chapter1_path.exists():
    all_docs.append({
        'Category': '4 - General Provisions (Ch 1)',
        'Appendix_Number': '',
        'Subfolder': '',
        'Filename': 'Chapter 1.docx',
        'File_Type': '.DOCX',
        'Size_MB': f"{chapter1_path.stat().st_size / (1024*1024):.2f}",
        'Modified_Date': datetime.fromtimestamp(chapter1_path.stat().st_mtime).strftime('%Y-%m-%d'),
        'Full_Path': str(chapter1_path),
        'Priority': 'CRITICAL',
        'Notes': 'Already reviewed - source of closeout requirements CSV'
    })

print(f"✅ Added General Provisions (Ch 1)")

# ==============================================================================
# 5. COMMUNITY WORKFORCE AGREEMENT
# ==============================================================================

cwa_path = Path("/Users/z/Library/CloudStorage/OneDrive-WashingtonStateDepartmentofTransportation/TheBRIDGE - Montlake - Change Management  Documents/120_RFP Conformed to COs/Appendices/Z - Community Workforce Agreement")
if cwa_path.exists():
    for cwa_file in sorted(cwa_path.rglob("*.pdf")):
        all_docs.append({
            'Category': '5 - Community Workforce Agreement',
            'Appendix_Number': 'Z1',
            'Subfolder': str(cwa_file.parent.relative_to(cwa_path)),
            'Filename': cwa_file.name,
            'File_Type': '.PDF',
            'Size_MB': f"{cwa_file.stat().st_size / (1024*1024):.2f}",
            'Modified_Date': datetime.fromtimestamp(cwa_file.stat().st_mtime).strftime('%Y-%m-%d'),
            'Full_Path': str(cwa_file),
            'Priority': 'MEDIUM',
            'Notes': ''
        })

print(f"✅ Added Community Workforce Agreement")

# ==============================================================================
# 6. TECHNICAL REQUIREMENTS (Chapter 2)
# ==============================================================================

chapter2_path = Path("/Users/z/Library/CloudStorage/OneDrive-WashingtonStateDepartmentofTransportation/TheBRIDGE - Montlake - Change Management  Documents/120_RFP Conformed to COs/Chapter Two.docx")
if chapter2_path.exists():
    all_docs.append({
        'Category': '6 - Technical Requirements (Ch 2)',
        'Appendix_Number': '',
        'Subfolder': '',
        'Filename': 'Chapter Two.docx',
        'File_Type': '.DOCX',
        'Size_MB': f"{chapter2_path.stat().st_size / (1024*1024):.2f}",
        'Modified_Date': datetime.fromtimestamp(chapter2_path.stat().st_mtime).strftime('%Y-%m-%d'),
        'Full_Path': str(chapter2_path),
        'Priority': 'CRITICAL',
        'Notes': 'Already reviewed - source of closeout requirements CSV'
    })

print(f"✅ Added Technical Requirements (Ch 2)")

# ==============================================================================
# 7. RFP APPENDICES (A-Z)
# ==============================================================================

# Rename appendices to show they're part of item 7
appendices_df['Category'] = '7 - Appendices: ' + appendices_df['Category']

# Assign priority for appendices
def assign_appendix_priority(category):
    if any(x in category for x in ['D - Manuals', 'V - Quality', 'A-B - As-Built', 'O - Design', 'E - Environmental', 'P - Permits']):
        return 'HIGH'
    elif any(x in category for x in ['U - Utilities', 'T - Traffic', 'I - Illumination', 'S - Structures', 'B - Spec', 'F - Forms', 'TF - Transit', 'C - Commit']):
        return 'MEDIUM'
    else:
        return 'LOW'

appendices_df['Priority'] = appendices_df['Category'].apply(assign_appendix_priority)
appendices_df['Notes'] = ''

print(f"✅ Added {len(appendices_df)} appendices")

# ==============================================================================
# 8. DESIGN-BUILDER'S PROPOSAL (3 Volumes)
# ==============================================================================

proposal_path = Path("/Users/z/Library/CloudStorage/OneDrive-WashingtonStateDepartmentofTransportation/TheBRIDGE - Montlake - Contract Documents/Design-Builder's Proposal/PDF DB Proposal")
if proposal_path.exists():
    for vol_file in sorted(proposal_path.glob("VOLUME *.pdf")):
        vol_num = 1 if "VOLUME 1" in vol_file.name else (2 if "VOLUME 2" in vol_file.name else 3)

        # Volume 2 contains Exhibit B
        notes = 'Contains Appendices A, B, C - EXHIBIT B (Betterments) is here' if vol_num == 2 else ''
        priority = 'CRITICAL' if vol_num == 2 else 'HIGH'

        all_docs.append({
            'Category': '8 - Design-Builder Proposal',
            'Appendix_Number': f'Volume {vol_num}',
            'Subfolder': '',
            'Filename': vol_file.name,
            'File_Type': '.PDF',
            'Size_MB': f"{vol_file.stat().st_size / (1024*1024):.2f}",
            'Modified_Date': datetime.fromtimestamp(vol_file.stat().st_mtime).strftime('%Y-%m-%d'),
            'Full_Path': str(vol_file),
            'Priority': priority,
            'Notes': notes
        })

print(f"✅ Added Design-Builder's Proposal (3 volumes)")

# ==============================================================================
# COMBINE ALL
# ==============================================================================

# Convert other docs to DataFrame
other_df = pd.DataFrame(all_docs)

# Combine with appendices
complete_df = pd.concat([other_df, appendices_df], ignore_index=True)

print()
print(f"✅ Total contract documents: {len(complete_df)}")
print()

# Add tracking columns
complete_df['Review_Status'] = 'Not Started'
complete_df['Reviewer'] = ''
complete_df['Review_Date'] = ''
complete_df['Closeout_Requirements_Found'] = ''
complete_df['Follow_Up_Required'] = ''

# Fill NaN values in Notes
complete_df['Notes'] = complete_df['Notes'].fillna('')

# Reorder columns
column_order = [
    'Priority',
    'Review_Status',
    'Category',
    'Appendix_Number',
    'Filename',
    'Subfolder',
    'File_Type',
    'Size_MB',
    'Modified_Date',
    'Closeout_Requirements_Found',
    'Notes',
    'Follow_Up_Required',
    'Reviewer',
    'Review_Date',
    'Full_Path'
]

complete_df = complete_df[column_order]

# Sort by Priority, then Category
priority_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
complete_df['Priority_Sort'] = complete_df['Priority'].map(priority_order)
complete_df = complete_df.sort_values(['Priority_Sort', 'Category', 'Filename'])
complete_df = complete_df.drop('Priority_Sort', axis=1)

# Save
output_file = '/Users/z/Desktop/git/montlake-closeout/contract_documents_complete_tracker.csv'
complete_df.to_csv(output_file, index=False)

print(f"💾 Saved complete tracker to: {output_file}")
print()

# Summary
print("=" * 80)
print("COMPLETE CONTRACT DOCUMENTS REVIEW TRACKER")
print("=" * 80)
print()

print("DOCUMENT COUNT BY CATEGORY:")
print("-" * 80)
category_counts = complete_df.groupby('Category').size().sort_index()
for cat, count in category_counts.items():
    priority = complete_df[complete_df['Category'] == cat]['Priority'].iloc[0]
    print(f"{priority:10} | {cat:55} | {count:4} docs")

print()
print("PRIORITY SUMMARY:")
print("-" * 80)
priority_counts = complete_df.groupby('Priority').size()
for priority in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
    if priority in priority_counts.index:
        count = priority_counts[priority]
        print(f"{priority:10} Priority: {count:5} documents")

print()
print("=" * 80)
print()
print("✅ Complete contract document review tracker created!")
print()
print("CRITICAL ITEMS TO REVIEW FIRST:")
print("  1. Change Orders 166-189 (24 COs)")
print("  2. General Provisions Ch 1 (already reviewed)")
print("  3. Technical Requirements Ch 2 (already reviewed)")
print("  4. Contract Form (contains contract terms)")
print("  5. DB's Proposal Vol 2 (contains EXHIBIT B - Betterments)")
print()
print("ISSUES TO NOTE:")
print(f"  • CO 044: Completely missing")
print(f"  • COs 001-042, 187-188: Folders exist but no executed PDFs")
print()
