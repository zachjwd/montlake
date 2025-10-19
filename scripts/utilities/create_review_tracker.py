#!/usr/bin/env python3
"""
Create appendix review tracking spreadsheet
Adds review status and priority to the inventory
"""

import pandas as pd
from datetime import datetime

# Read the inventory
print("📊 Creating Appendix Review Tracker...")
print()

df = pd.read_csv('/Users/z/Desktop/git/montlake-closeout/appendices_inventory.csv')

print(f"✅ Loaded {len(df)} appendices")
print()

# Define priority based on category and likely closeout relevance
def assign_priority(row):
    """Assign priority based on category - higher priority = more likely to have closeout requirements"""

    category = row['Category']

    # HIGH PRIORITY - Most likely to contain closeout requirements
    high_priority = [
        'D - Manuals',  # O&M manuals, warranties
        'A-B - As-Built Plans and Construction',  # As-builts required for closeout
        'V - Quality Assurance',  # QA/QC records
        'O - Design Documentation',  # Design records
        'E - Environmental',  # Environmental compliance/permits
        'P - Permits and Approvals',  # Final permits and approvals
    ]

    # MEDIUM PRIORITY - May contain closeout requirements
    medium_priority = [
        'F - Forms',  # May have closeout forms
        'C - Commitments List',  # Track commitments
        'B - Specifications',  # Reference specs
        'U - Utilities',  # Utility as-builts and documentation
        'S - Structures',  # Structural documentation
        'I - Illumination, Electrical & ITS',  # System documentation
        'T - Traffic',  # Traffic system documentation
        'TF - Transit Facilities',  # Transit documentation
    ]

    # LOW PRIORITY - Less likely to have specific closeout requirements
    low_priority = [
        'A - Project Files',  # Reference only
        'G - Geotechnical',  # Background info
        'H - Hydraulics',  # Background info
        'J - Pavement',  # Background info
        'K - Prevailing Wages Information',  # Handled in Ch 1
        'L - Landscape and Urban Design',  # Design reference
        'M - Conceptual Plans',  # Design reference
        'N - Local Agency Agreements',  # Agreements (may need review)
        'R - Right-of-Way',  # ROW docs
        'X - Montlake Underlid Systems',  # System documentation
        'Y - Montlake Phase Communications Plan',  # Communications
        'Z - Community Workforce Agreement',  # CWA documentation
        'Q - Intentionally Omitted',
        'W - Intentionally Omitted',
    ]

    if category in high_priority:
        return 'HIGH'
    elif category in medium_priority:
        return 'MEDIUM'
    elif category in low_priority:
        return 'LOW'
    else:
        return 'MEDIUM'  # Default

# Add tracking columns
df['Priority'] = df.apply(assign_priority, axis=1)
df['Review_Status'] = 'Not Started'
df['Reviewer'] = ''
df['Review_Date'] = ''
df['Closeout_Requirements_Found'] = ''
df['Notes'] = ''
df['Follow_Up_Required'] = ''

# Reorder columns for better usability
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

df = df[column_order]

# Sort by Priority (HIGH first), then Category
priority_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
df['Priority_Sort'] = df['Priority'].map(priority_order)
df = df.sort_values(['Priority_Sort', 'Category', 'Appendix_Number', 'Filename'])
df = df.drop('Priority_Sort', axis=1)

# Save tracking spreadsheet
output_file = '/Users/z/Desktop/git/montlake-closeout/appendices_review_tracker.csv'
df.to_csv(output_file, index=False)

print(f"💾 Saved review tracker to: {output_file}")
print()

# Create summary by priority
print("📊 PRIORITY SUMMARY:")
print("=" * 60)
priority_counts = df.groupby('Priority').size()
for priority in ['HIGH', 'MEDIUM', 'LOW']:
    if priority in priority_counts.index:
        count = priority_counts[priority]
        print(f"{priority:8} Priority: {count:4} files")

print()
print("=" * 60)

# Show categories by priority
print()
print("📋 CATEGORIES BY PRIORITY:")
print("=" * 60)
print()

for priority in ['HIGH', 'MEDIUM', 'LOW']:
    priority_df = df[df['Priority'] == priority]
    if len(priority_df) > 0:
        print(f"{priority} PRIORITY:")
        categories = priority_df.groupby('Category').size().sort_values(ascending=False)
        for cat, count in categories.items():
            print(f"  • {cat}: {count} files")
        print()

print("=" * 60)
print()
print("✅ Review tracker created!")
print()
print("COLUMNS IN TRACKER:")
print("  • Priority: HIGH/MEDIUM/LOW")
print("  • Review_Status: Not Started/In Progress/Reviewed/N/A")
print("  • Category: Appendix category")
print("  • Appendix_Number: Appendix ID")
print("  • Filename: File name")
print("  • Closeout_Requirements_Found: Summary of requirements")
print("  • Notes: Any observations")
print("  • Follow_Up_Required: Yes/No")
print("  • Reviewer: Who reviewed")
print("  • Review_Date: When reviewed")
print()
print("SUGGESTED STATUSES:")
print("  • Not Started - Haven't looked at it yet")
print("  • In Progress - Currently reviewing")
print("  • Reviewed - Completed review")
print("  • N/A - Not applicable for closeout")
print()
print("You can now open this CSV in Excel and track your progress!")
print()
