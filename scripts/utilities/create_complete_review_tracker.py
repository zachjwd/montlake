#!/usr/bin/env python3
"""
Create COMPLETE contract document review tracker
Includes all contract documents, not just appendices
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

print("📊 Creating Complete Contract Document Review Tracker...")
print()

# Load existing appendices inventory
appendices_df = pd.read_csv('/Users/z/Desktop/git/montlake-closeout/appendices_inventory.csv')

print(f"✅ Loaded {len(appendices_df)} appendices")

# Define other contract documents
other_docs = []

# Base path
base_path = Path("/Users/z/Library/CloudStorage/OneDrive-WashingtonStateDepartmentofTransportation/TheBRIDGE - Montlake - Change Management  Documents")
rfp_path = base_path / "120_RFP Conformed to COs"
co_path = base_path / "050_Change Orders"

# 1. Change Orders - we already have these downloaded
co_folder = Path("/Users/z/Desktop/git/Change Orders 166-189")
if co_folder.exists():
    for co_file in sorted(co_folder.glob("*.pdf")):
        other_docs.append({
            'Category': '1 - Change Orders',
            'Appendix_Number': '',
            'Subfolder': 'Change Orders 166-189',
            'Filename': co_file.name,
            'File_Type': '.PDF',
            'Size_MB': f"{co_file.stat().st_size / (1024*1024):.2f}",
            'Modified_Date': datetime.fromtimestamp(co_file.stat().st_mtime).strftime('%Y-%m-%d'),
            'Full_Path': str(co_file)
        })

# 2. Contract Form
contract_form = rfp_path / "Contract Form.docx"
if contract_form.exists():
    other_docs.append({
        'Category': '2 - Contract Form',
        'Appendix_Number': '',
        'Subfolder': '',
        'Filename': 'Contract Form.docx',
        'File_Type': '.DOCX',
        'Size_MB': f"{contract_form.stat().st_size / (1024*1024):.2f}",
        'Modified_Date': datetime.fromtimestamp(contract_form.stat().st_mtime).strftime('%Y-%m-%d'),
        'Full_Path': str(contract_form)
    })

# 3. Exhibit B - WSDOT Identified Betterments (need to find)
# This is typically in the proposal or contract form - placeholder for now
other_docs.append({
    'Category': '3 - Exhibit B (Betterments)',
    'Appendix_Number': '',
    'Subfolder': '',
    'Filename': 'Exhibit B - WSDOT Identified Betterments',
    'File_Type': 'TBD',
    'Size_MB': '0.00',
    'Modified_Date': '',
    'Full_Path': 'TO BE LOCATED'
})

# 4. General Provisions - RFP Chapter 1
chapter1 = rfp_path / "Chapter 1.docx"
if chapter1.exists():
    other_docs.append({
        'Category': '4 - General Provisions (Ch 1)',
        'Appendix_Number': '',
        'Subfolder': '',
        'Filename': 'Chapter 1.docx',
        'File_Type': '.DOCX',
        'Size_MB': f"{chapter1.stat().st_size / (1024*1024):.2f}",
        'Modified_Date': datetime.fromtimestamp(chapter1.stat().st_mtime).strftime('%Y-%m-%d'),
        'Full_Path': str(chapter1)
    })

# 5. Community Workforce Agreement
cwa_path = rfp_path / "Appendices" / "Z - Community Workforce Agreement"
if cwa_path.exists():
    for cwa_file in sorted(cwa_path.rglob("*.pdf")):
        other_docs.append({
            'Category': '5 - Community Workforce Agreement',
            'Appendix_Number': 'Z1',
            'Subfolder': str(cwa_file.parent.relative_to(cwa_path)),
            'Filename': cwa_file.name,
            'File_Type': '.PDF',
            'Size_MB': f"{cwa_file.stat().st_size / (1024*1024):.2f}",
            'Modified_Date': datetime.fromtimestamp(cwa_file.stat().st_mtime).strftime('%Y-%m-%d'),
            'Full_Path': str(cwa_file)
        })

# 6. Technical Requirements - RFP Chapter 2
chapter2 = rfp_path / "Chapter Two.docx"
if chapter2.exists():
    other_docs.append({
        'Category': '6 - Technical Requirements (Ch 2)',
        'Appendix_Number': '',
        'Subfolder': '',
        'Filename': 'Chapter Two.docx',
        'File_Type': '.DOCX',
        'Size_MB': f"{chapter2.stat().st_size / (1024*1024):.2f}",
        'Modified_Date': datetime.fromtimestamp(chapter2.stat().st_mtime).strftime('%Y-%m-%d'),
        'Full_Path': str(chapter2)
    })

# 7. Appendices are already included in appendices_df

# 8. Design-Builder's Proposal Documents (need to locate)
other_docs.append({
    'Category': '8 - Design-Builder Proposal',
    'Appendix_Number': '',
    'Subfolder': '',
    'Filename': 'Design-Builder Proposal Documents',
    'File_Type': 'TBD',
    'Size_MB': '0.00',
    'Modified_Date': '',
    'Full_Path': 'TO BE LOCATED'
})

# Create DataFrame for other documents
other_df = pd.DataFrame(other_docs)

print(f"✅ Found {len(other_df)} other contract documents")
print()

# Combine appendices with other documents
# First, rename appendices category to show it's item 7
appendices_df['Category'] = '7 - ' + appendices_df['Category']

# Combine
all_docs = pd.concat([other_df, appendices_df], ignore_index=True)

print(f"✅ Total contract documents: {len(all_docs)}")
print()

# Assign priority
def assign_priority(row):
    """Assign priority for ALL contract documents"""

    category = row['Category']

    # CRITICAL - Must review for closeout
    critical = [
        '4 - General Provisions (Ch 1)',  # Section 1-04, 1-05, 1-08, 1-09 have closeout reqs
        '6 - Technical Requirements (Ch 2)',  # Section 2.12 has documentation requirements
        '1 - Change Orders',  # All COs may affect closeout
    ]

    # HIGH PRIORITY
    high_priority = [
        '7 - D - Manuals',
        '7 - A-B - As-Built Plans and Construction',
        '7 - V - Quality Assurance',
        '7 - O - Design Documentation',
        '7 - E - Environmental',
        '7 - P - Permits and Approvals',
    ]

    # MEDIUM PRIORITY
    medium_priority = [
        '2 - Contract Form',
        '3 - Exhibit B (Betterments)',
        '5 - Community Workforce Agreement',
        '8 - Design-Builder Proposal',
        '7 - F - Forms',
        '7 - C - Commitments List',
        '7 - B - Specifications',
        '7 - U - Utilities',
        '7 - S - Structures',
        '7 - I - Illumination, Electrical & ITS',
        '7 - T - Traffic',
        '7 - TF - Transit Facilities',
    ]

    if category in critical:
        return 'CRITICAL'
    elif category in high_priority:
        return 'HIGH'
    elif category in medium_priority:
        return 'MEDIUM'
    else:
        return 'LOW'

# Add tracking columns
all_docs['Priority'] = all_docs.apply(assign_priority, axis=1)
all_docs['Review_Status'] = 'Not Started'
all_docs['Reviewer'] = ''
all_docs['Review_Date'] = ''
all_docs['Closeout_Requirements_Found'] = ''
all_docs['Notes'] = ''
all_docs['Follow_Up_Required'] = ''

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

all_docs = all_docs[column_order]

# Sort by Priority, then Category
priority_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
all_docs['Priority_Sort'] = all_docs['Priority'].map(priority_order)
all_docs = all_docs.sort_values(['Priority_Sort', 'Category', 'Filename'])
all_docs = all_docs.drop('Priority_Sort', axis=1)

# Save
output_file = '/Users/z/Desktop/git/montlake-closeout/contract_documents_review_tracker.csv'
all_docs.to_csv(output_file, index=False)

print(f"💾 Saved complete tracker to: {output_file}")
print()

# Summary
print("=" * 80)
print("COMPLETE CONTRACT DOCUMENTS REVIEW TRACKER")
print("=" * 80)
print()

print("PRIORITY SUMMARY:")
print("-" * 80)
priority_counts = all_docs.groupby('Priority').size()
for priority in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
    if priority in priority_counts.index:
        count = priority_counts[priority]
        print(f"{priority:10} Priority: {count:5} documents")
print()

print("CONTRACT DOCUMENT CATEGORIES:")
print("-" * 80)
print()

# Group by main category number
all_docs['Main_Category'] = all_docs['Category'].str.split(' - ').str[0]
category_groups = all_docs.groupby('Main_Category').agg({
    'Category': 'first',
    'Priority': 'first',
    'Filename': 'count'
}).rename(columns={'Filename': 'Count'})

for idx, row in category_groups.iterrows():
    print(f"{row['Priority']:10} | {row['Category']:50} | {row['Count']:4} docs")

print()
print("=" * 80)
print()
print("✅ Complete contract document review tracker created!")
print()
print("START WITH CRITICAL ITEMS:")
print("  1. General Provisions (Ch 1) - Has most closeout requirements")
print("  2. Technical Requirements (Ch 2) - Documentation requirements")
print("  3. Change Orders 166-189 - May modify closeout requirements")
print()
