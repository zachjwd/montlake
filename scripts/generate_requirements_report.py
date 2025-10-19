#!/usr/bin/env python3
"""
Generate Closeout Requirements Coverage Report
Shows which of the 784 required documents we have vs. missing
"""

import pandas as pd
from datetime import datetime

print("📊 Generating Closeout Requirements Coverage Report...")
print()

# Load requirements and tracker
req_df = pd.read_csv('/Users/z/Downloads/Montlake Docs - Sheet1 (2).csv')
tracker_df = pd.read_csv('data/contract_documents_complete_tracker.csv', encoding='utf-8-sig')

print(f"✅ Loaded {len(req_df)} required closeout documents")
print(f"✅ Loaded {len(tracker_df)} documents from tracker")
print()

# Format doc numbers
req_df['Doc_Number'] = req_df['document_number'].apply(lambda x: f"{int(x):03d}")

# Get unique doc numbers in tracker (convert to strings with leading zeros)
tracker_doc_nums = set()
for num in tracker_df['Doc_Number'].unique():
    if pd.notna(num) and str(num) != '':
        # Convert to 3-digit string with leading zeros
        tracker_doc_nums.add(f"{int(num):03d}")

# Categorize requirements
requirements_status = []
for _, req in req_df.iterrows():
    doc_num = req['Doc_Number']

    # Check if we have this document
    if doc_num in tracker_doc_nums:
        # Get review status of documents with this doc number
        matching_docs = tracker_df[tracker_df['Doc_Number'] == doc_num]
        reviewed = len(matching_docs[matching_docs['Review_Status'] == 'Reviewed'])
        total = len(matching_docs)

        if reviewed == total:
            status = 'Complete'
        elif reviewed > 0:
            status = 'In Progress'
        else:
            status = 'Have Document'
    else:
        status = 'Missing'

    requirements_status.append({
        'Doc_Number': doc_num,
        'Document_Name': req['document_name'],
        'Category': req['category'],
        'Document_Type': req['document_type'],
        'Status': status,
        'Notes': req['notes'] if pd.notna(req['notes']) else ''
    })

req_status_df = pd.DataFrame(requirements_status)

# Calculate statistics
total_reqs = len(req_status_df)
complete = len(req_status_df[req_status_df['Status'] == 'Complete'])
in_progress = len(req_status_df[req_status_df['Status'] == 'In Progress'])
have_doc = len(req_status_df[req_status_df['Status'] == 'Have Document'])
missing = len(req_status_df[req_status_df['Status'] == 'Missing'])

have_total = complete + in_progress + have_doc
pct_have = (have_total / total_reqs * 100)
pct_reviewed = (complete / total_reqs * 100)

print("=" * 80)
print("CLOSEOUT REQUIREMENTS COVERAGE")
print("=" * 80)
print()
print(f"Total Required Documents:      {total_reqs}")
print(f"  ✅ Complete (Reviewed):       {complete:4} ({complete/total_reqs*100:5.1f}%)")
print(f"  🔄 In Progress:               {in_progress:4} ({in_progress/total_reqs*100:5.1f}%)")
print(f"  📄 Have Document (Not Rev):   {have_doc:4} ({have_doc/total_reqs*100:5.1f}%)")
print(f"  ❌ Missing:                   {missing:4} ({missing/total_reqs*100:5.1f}%)")
print()
print(f"📦 Documents We Have:          {have_total}/{total_reqs} ({pct_have:.1f}%)")
print(f"✅ Requirements Reviewed:      {complete}/{total_reqs} ({pct_reviewed:.1f}%)")
print()

# Breakdown by document type
print("COVERAGE BY DOCUMENT TYPE:")
print("-" * 80)
for doc_type in ['Standard', 'ChangeOrder', 'Appendix']:
    type_reqs = req_status_df[req_status_df['Document_Type'] == doc_type]
    type_total = len(type_reqs)
    type_have = len(type_reqs[type_reqs['Status'] != 'Missing'])
    type_complete = len(type_reqs[type_reqs['Status'] == 'Complete'])

    if type_total > 0:
        print(f"{doc_type:15} {type_have:3}/{type_total:3} have ({type_have/type_total*100:5.1f}%) | "
              f"{type_complete:3} complete ({type_complete/type_total*100:5.1f}%)")

print()

# Show missing documents by category
print("MISSING DOCUMENTS BY CATEGORY:")
print("-" * 80)
missing_docs = req_status_df[req_status_df['Status'] == 'Missing']
if len(missing_docs) > 0:
    missing_by_cat = missing_docs.groupby('Category').size().sort_values(ascending=False)
    for cat, count in missing_by_cat.head(15).items():
        print(f"  {cat:45} {count:3} missing")
else:
    print("  None - We have all required documents!")

print()

# Save detailed report
req_status_df.to_csv('reports/closeout_requirements_coverage.csv', index=False)
print(f"💾 Saved detailed report: reports/closeout_requirements_coverage.csv")

# Save missing documents list
missing_docs.to_csv('reports/missing_closeout_requirements.csv', index=False)
print(f"💾 Saved missing docs list: reports/missing_closeout_requirements.csv ({len(missing_docs)} docs)")

print()
print("✅ Requirements coverage report complete!")
print()
