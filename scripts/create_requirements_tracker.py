#!/usr/bin/env python3
"""
Create requirements-based tracker
Uses the 784 required deliverables as the master list
Links to actual files when we have them
"""

import pandas as pd

print("📋 Creating Requirements-Based Tracker...")
print()

# Load requirements (the 784 deliverables)
req_df = pd.read_csv('/Users/z/Downloads/Montlake Docs - Sheet1 (2).csv')
print(f"✅ Loaded {len(req_df)} required deliverables")

# Load current tracker (with files)
tracker_df = pd.read_csv('data/contract_documents_complete_tracker.csv', encoding='utf-8-sig')
print(f"✅ Loaded {len(tracker_df)} files from tracker")

# Filter out cover sheets from tracker
tracker_df = tracker_df[~tracker_df['Filename'].str.contains('Cover Sheet', case=False, na=False)]
print(f"✅ Filtered to {len(tracker_df)} non-cover-sheet files")
print()

# Format Doc_Number in requirements
req_df['Doc_Number'] = req_df['document_number'].apply(lambda x: f"{int(x):03d}")

# Convert tracker Doc_Number to string for matching
tracker_df['Doc_Number'] = tracker_df['Doc_Number'].astype(str).str.zfill(3)

# Map Contract Section
def get_contract_section(doc_type, doc_num):
    """Map to the 8 contract sections"""
    if doc_type == 'ChangeOrder':
        return '1. Change Orders and Supplemental Agreements'
    elif doc_num == 3:
        return '2. Design-Build Contract (Contract Form)'
    elif doc_num == 6:  # Exhibit B
        return '3. WSDOT-Identified Betterments (Exhibit B)'
    elif doc_num == 1:
        return '4. General Provisions (RFP Chapter 1)'
    elif doc_num == 4:
        return '5. Community Workforce Agreement (CWA)'
    elif doc_num == 2:
        return '6. Technical Requirements (RFP Chapter 2)'
    elif doc_num == 5 or doc_num == 7:
        return '8. Design-Builder\'s Proposal Documents'
    else:  # Appendices
        return '7. RFP Appendices (Contract Documents)'

req_df['Contract_Section'] = req_df.apply(
    lambda row: get_contract_section(row['document_type'], row['document_number']),
    axis=1
)

# Create requirements tracker
requirements_tracker = []

print("🔄 Linking requirements to files...")
print()

for _, req in req_df.iterrows():
    doc_num = req['Doc_Number']

    # Find matching files in tracker
    matching_files = tracker_df[tracker_df['Doc_Number'] == doc_num]

    if len(matching_files) > 0:
        # We have file(s) for this requirement
        # Get review status from files
        reviewed = len(matching_files[matching_files['Review_Status'] == 'Reviewed'])
        total_files = len(matching_files)

        if reviewed == total_files:
            review_status = 'Reviewed'
        elif reviewed > 0:
            review_status = 'In Progress'
        else:
            review_status = 'Not Started'

        # Get file info (use first file as representative)
        first_file = matching_files.iloc[0]

        requirements_tracker.append({
            'Doc_Number': doc_num,
            'Document_Name': req['document_name'],
            'Full_Name': req['full_name'] if pd.notna(req['full_name']) else '',
            'Category': req['category'],
            'Document_Type': req['document_type'],
            'Contract_Section': req['Contract_Section'],
            'Review_Status': review_status,
            'Notes': req['notes'] if pd.notna(req['notes']) else '',
            'Files_Count': total_files,
            'Representative_File': first_file['Filename'],
            'File_Path': first_file['Full_Path'] if 'Full_Path' in first_file else ''
        })
    else:
        # We don't have this requirement
        requirements_tracker.append({
            'Doc_Number': doc_num,
            'Document_Name': req['document_name'],
            'Full_Name': req['full_name'] if pd.notna(req['full_name']) else '',
            'Category': req['category'],
            'Document_Type': req['document_type'],
            'Contract_Section': req['Contract_Section'],
            'Review_Status': 'Not Started',
            'Notes': req['notes'] if pd.notna(req['notes']) else '',
            'Files_Count': 0,
            'Representative_File': '',
            'File_Path': ''
        })

requirements_tracker_df = pd.DataFrame(requirements_tracker)

# Save the requirements tracker
requirements_tracker_df.to_csv('data/requirements_tracker.csv', index=False)
print(f"💾 Saved requirements tracker: data/requirements_tracker.csv")
print()

# Statistics
print("=" * 100)
print("REQUIREMENTS COVERAGE")
print("=" * 100)
total = len(requirements_tracker_df)
reviewed = len(requirements_tracker_df[requirements_tracker_df['Review_Status'] == 'Reviewed'])
in_progress = len(requirements_tracker_df[requirements_tracker_df['Review_Status'] == 'In Progress'])
not_started = len(requirements_tracker_df[requirements_tracker_df['Review_Status'] == 'Not Started'])
have_files = len(requirements_tracker_df[requirements_tracker_df['Files_Count'] > 0])

print(f"Total Required Deliverables:    {total}")
print(f"  ✅ Reviewed:                   {reviewed:4} ({reviewed/total*100:5.1f}%)")
print(f"  🔄 In Progress:                {in_progress:4} ({in_progress/total*100:5.1f}%)")
print(f"  📋 Not Started:                {not_started:4} ({not_started/total*100:5.1f}%)")
print()
print(f"📦 Deliverables We Have Files:   {have_files}/{total} ({have_files/total*100:.1f}%)")
print(f"✅ Deliverables Reviewed:        {reviewed}/{total} ({reviewed/total*100:.1f}%)")
print()

# Coverage by Contract Section
print("COVERAGE BY CONTRACT SECTION:")
print("-" * 100)
for section in sorted(requirements_tracker_df['Contract_Section'].unique()):
    section_reqs = requirements_tracker_df[requirements_tracker_df['Contract_Section'] == section]
    section_total = len(section_reqs)
    section_have = len(section_reqs[section_reqs['Files_Count'] > 0])
    section_reviewed = len(section_reqs[section_reqs['Review_Status'] == 'Reviewed'])

    print(f"{section}")
    print(f"  {section_have}/{section_total} have files ({section_have/section_total*100:.1f}%) | "
          f"{section_reviewed} reviewed ({section_reviewed/section_total*100:.1f}%)")

print()
print("✅ Requirements tracker created!")
print()
