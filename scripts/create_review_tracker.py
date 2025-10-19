#!/usr/bin/env python3
"""
Create Review-Focused Tracker
Marks all 741 files we have as either "Reviewed" or "Needs Review"
Adds descriptive names from requirements where available
"""

import pandas as pd

print("📋 Creating Review-Focused Tracker...")
print()

# Load current tracker (with files)
tracker_df = pd.read_csv('data/contract_documents_complete_tracker.csv', encoding='utf-8-sig')
print(f"✅ Loaded {len(tracker_df)} files from tracker")

# Filter out cover sheets
tracker_df = tracker_df[~tracker_df['Filename'].str.contains('Cover Sheet', case=False, na=False)]
print(f"✅ Filtered to {len(tracker_df)} non-cover-sheet files")

# Load requirements for descriptive names
req_df = pd.read_csv('/Users/z/Downloads/Montlake Docs - Sheet1 (2).csv')
req_df['Doc_Number'] = req_df['document_number'].apply(lambda x: f"{int(x):03d}")
print(f"✅ Loaded {len(req_df)} requirements for reference")
print()

# Convert tracker Doc_Number to string for matching
tracker_df['Doc_Number'] = tracker_df['Doc_Number'].astype(str).str.zfill(3)

# Map Contract Section
def assign_contract_section(row):
    """Map to the 8 contract sections"""
    category = str(row['Category']).lower()

    if 'change orders' in category:
        return '1. Change Orders and Supplemental Agreements'
    elif 'contract form' in category:
        return '2. Design-Build Contract (Contract Form)'
    elif 'design-builder proposal' in category and 'volume 2' in str(row['Appendix_Number']).lower():
        return '3. WSDOT-Identified Betterments (Exhibit B)'
    elif 'general provisions' in category or 'chapter 1' in category or 'ch 1' in category:
        return '4. General Provisions (RFP Chapter 1)'
    elif 'workforce agreement' in category:
        return '5. Community Workforce Agreement (CWA)'
    elif 'technical requirements' in category or 'chapter 2' in category or 'ch 2' in category:
        return '6. Technical Requirements (RFP Chapter 2)'
    elif 'design-builder proposal' in category:
        return '8. Design-Builder\'s Proposal Documents'
    else:
        return '7. RFP Appendices (Contract Documents)'

tracker_df['Contract_Section'] = tracker_df.apply(assign_contract_section, axis=1)

# Add descriptive document names where we can match
tracker_df['Document_Name'] = ''
for idx, row in tracker_df.iterrows():
    doc_num = row['Doc_Number']

    # Try to find matching requirement
    req_match = req_df[req_df['Doc_Number'] == doc_num]
    if len(req_match) > 0:
        tracker_df.at[idx, 'Document_Name'] = req_match.iloc[0]['document_name']
    else:
        # Use filename as fallback
        tracker_df.at[idx, 'Document_Name'] = row['Filename'].replace('.pdf', '').replace('.PDF', '')

# Simplify review status
def simplify_status(status):
    if status == 'Reviewed':
        return 'Reviewed'
    else:
        return 'Needs Review'

tracker_df['Review_Status'] = tracker_df['Review_Status'].apply(simplify_status)

# Add Notes column if it doesn't exist
if 'Notes' not in tracker_df.columns:
    tracker_df['Notes'] = ''

# Reorder columns for clarity
columns = [
    'Doc_Number',
    'Document_Name',
    'Contract_Section',
    'Category',
    'Review_Status',
    'Notes',
    'Filename',
    'Appendix_Number',
    'Priority',
    'Document_Type',
    'File_Type',
    'Size_MB',
    'Modified_Date',
    'Full_Path'
]

# Only include columns that exist
columns = [col for col in columns if col in tracker_df.columns]
tracker_df = tracker_df[columns]

# Save review tracker
tracker_df.to_csv('data/review_tracker.csv', index=False)
print(f"💾 Saved review tracker: data/review_tracker.csv")
print()

# Statistics
print("=" * 100)
print("REVIEW TRACKER SUMMARY")
print("=" * 100)
total = len(tracker_df)
reviewed = len(tracker_df[tracker_df['Review_Status'] == 'Reviewed'])
needs_review = len(tracker_df[tracker_df['Review_Status'] == 'Needs Review'])

print(f"Total Documents:        {total}")
print(f"  ✅ Reviewed:          {reviewed:4} ({reviewed/total*100:5.1f}%)")
print(f"  📋 Needs Review:      {needs_review:4} ({needs_review/total*100:5.1f}%)")
print()

# By Contract Section
print("REVIEW STATUS BY CONTRACT SECTION:")
print("-" * 100)
for section in sorted(tracker_df['Contract_Section'].unique()):
    section_docs = tracker_df[tracker_df['Contract_Section'] == section]
    section_total = len(section_docs)
    section_reviewed = len(section_docs[section_docs['Review_Status'] == 'Reviewed'])

    print(f"{section}")
    print(f"  {section_reviewed}/{section_total} reviewed ({section_reviewed/section_total*100:.1f}%)")

print()

# Section-weighted progress
sections = tracker_df['Contract_Section'].unique()
sections_complete = 0
section_progress_sum = 0

for section in sections:
    section_docs = tracker_df[tracker_df['Contract_Section'] == section]
    section_total = len(section_docs)
    section_reviewed = len(section_docs[section_docs['Review_Status'] == 'Reviewed'])
    section_pct = section_reviewed / section_total if section_total > 0 else 0
    section_progress_sum += section_pct

    if section_reviewed == section_total:
        sections_complete += 1

overall_section_weighted = (section_progress_sum / len(sections)) * 100

print(f"📊 Section-Weighted Progress: {overall_section_weighted:.1f}%")
print(f"📊 Sections Complete: {sections_complete}/{len(sections)}")
print()
print("✅ Review tracker created!")
print()
