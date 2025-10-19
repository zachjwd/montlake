#!/usr/bin/env python3
"""
Apply Doc_Numbers to the tracker CSV
"""

import pandas as pd

print("📝 Applying Doc_Numbers to tracker...")
print()

# Load tracker and matches
tracker_df = pd.read_csv('data/contract_documents_complete_tracker.csv', encoding='utf-8-sig')
matches_df = pd.read_csv('reports/matched_requirements.csv')

print(f"✅ Loaded {len(tracker_df)} documents from tracker")
print(f"✅ Loaded {len(matches_df)} matches")
print()

# Create a mapping of tracker_idx to doc_number
doc_number_map = {}
for _, match in matches_df.iterrows():
    doc_number_map[match['tracker_idx']] = match['doc_number']

# Add Doc_Number column
tracker_df['Doc_Number'] = ''
for idx, row in tracker_df.iterrows():
    if idx in doc_number_map:
        tracker_df.at[idx, 'Doc_Number'] = doc_number_map[idx]

# Count how many got doc numbers
with_doc_num = len(tracker_df[tracker_df['Doc_Number'] != ''])
print(f"✅ Applied Doc_Number to {with_doc_num}/{len(tracker_df)} documents ({with_doc_num/len(tracker_df)*100:.1f}%)")
print()

# Reorder columns to put Doc_Number near the front
columns = list(tracker_df.columns)
columns.remove('Doc_Number')
columns.insert(0, 'Doc_Number')  # Put at the very beginning
tracker_df = tracker_df[columns]

# Save updated tracker
tracker_df.to_csv('data/contract_documents_complete_tracker.csv', index=False)
print(f"💾 Saved updated tracker with Doc_Number column")
print()

# Show samples
print("📋 Sample Doc_Numbers assigned:")
print("-" * 80)
samples = tracker_df[tracker_df['Doc_Number'] != ''].head(10)
for _, row in samples.iterrows():
    print(f"Doc {row['Doc_Number']}: {row['Filename'][:60]}")
    print(f"         {row['Category'][:50]}")
    print()

print("✅ Complete! Tracker now has Doc_Number for all documents")
print()
