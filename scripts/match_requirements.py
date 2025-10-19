#!/usr/bin/env python3
"""
Match documents in tracker to closeout requirements
Add Document Number (formatted as 3 digits) to tracker
"""

import pandas as pd
import re

print("🔍 Matching documents to closeout requirements...")
print()

# Load both files
tracker_df = pd.read_csv('data/contract_documents_complete_tracker.csv', encoding='utf-8-sig')
req_df = pd.read_csv('/Users/z/Downloads/Montlake Docs - Sheet1 (2).csv')

print(f"✅ Loaded {len(tracker_df)} documents from tracker")
print(f"✅ Loaded {len(req_df)} required closeout documents")
print()

# Format document_number as 3 digits with leading zeros
req_df['Doc_Number'] = req_df['document_number'].apply(lambda x: f"{int(x):03d}")

# Clean up names for matching
def clean_name(name):
    """Normalize document names for matching"""
    if pd.isna(name):
        return ""
    name = str(name).lower().strip()
    # Remove common variations
    name = re.sub(r'\s+', ' ', name)
    name = name.replace('appendix ', '')
    name = name.replace('appendices: ', '')
    name = name.replace('7 - ', '')
    name = name.replace('1 - ', '')
    name = name.replace('2 - ', '')
    name = name.replace('4 - ', '')
    name = name.replace('5 - ', '')
    name = name.replace('6 - ', '')
    name = name.replace('8 - ', '')
    return name

# Add cleaned names
tracker_df['clean_name'] = tracker_df['Filename'].apply(clean_name)
tracker_df['clean_category'] = tracker_df['Category'].apply(clean_name)
req_df['clean_doc_name'] = req_df['document_name'].apply(clean_name)
req_df['clean_category'] = req_df['category'].apply(clean_name)

# Initialize Doc_Number column in tracker
tracker_df['Doc_Number'] = ''

# Match documents
matches = []
unmatched_tracker = []
unmatched_requirements = []

# Track which requirements we've matched
matched_doc_numbers = set()

print("🔄 Matching documents...")
print()

for idx, tracker_row in tracker_df.iterrows():
    best_match = None
    best_score = 0

    # Special handling for Change Orders
    if tracker_row['Category'] == '1 - Change Orders':
        # Extract CO number from Appendix_Number (e.g., "CO 166")
        appendix = str(tracker_row['Appendix_Number'])
        if appendix.startswith('CO '):
            try:
                co_num = int(appendix.replace('CO ', ''))
                # Change Orders in requirements start at doc 700
                # CO 001 = Doc 700, CO 002 = Doc 701, etc.
                doc_num = 699 + co_num
                req_match = req_df[req_df['document_number'] == doc_num]
                if len(req_match) > 0:
                    best_match = req_match.iloc[0]
                    best_score = 15  # High confidence for CO matches
            except:
                pass

    # Special handling for Standard documents
    if best_match is None:
        category = tracker_row['Category']

        # Map standard documents
        if 'General Provisions' in category or 'Chapter 1' in category:
            best_match = req_df[req_df['document_number'] == 1].iloc[0]
            best_score = 15
        elif 'Technical Requirements' in category or 'Chapter 2' in category or 'Chapter Two' in category:
            best_match = req_df[req_df['document_number'] == 2].iloc[0]
            best_score = 15
        elif 'Contract Form' in category:
            best_match = req_df[req_df['document_number'] == 3].iloc[0]
            best_score = 15
        elif 'Community Workforce Agreement' in category and 'CWA' in tracker_row['Filename']:
            best_match = req_df[req_df['document_number'] == 4].iloc[0]
            best_score = 15
        elif 'Design-Builder Proposal' in category:
            best_match = req_df[req_df['document_number'] == 5].iloc[0]
            best_score = 15

    # Special handling for specific appendices by letter
    if best_match is None:
        category = tracker_row['Category']
        appendix = str(tracker_row['Appendix_Number'])

        # Appendix Y - Communications Plan maps to Doc 637
        if 'Y - ' in category and 'Communications' in category:
            req_match = req_df[req_df['document_number'] == 637]
            if len(req_match) > 0:
                best_match = req_match.iloc[0]
                best_score = 15

    # General matching for Appendices
    if best_match is None:
        for req_idx, req_row in req_df.iterrows():
            # Skip if already matched as a standard doc or CO
            if req_row['document_number'] <= 7 or req_row['document_number'] >= 700:
                continue

            score = 0

            # Category match is important
            if tracker_row['clean_category'] and req_row['clean_category']:
                if tracker_row['clean_category'] in req_row['clean_category'] or req_row['clean_category'] in tracker_row['clean_category']:
                    score += 3

            # Document name match
            tracker_name = tracker_row['clean_name']
            req_name = req_row['clean_doc_name']

            if tracker_name and req_name:
                # Exact match
                if tracker_name == req_name:
                    score += 10
                # Partial match
                elif tracker_name in req_name or req_name in tracker_name:
                    score += 5
                # Word overlap
                else:
                    tracker_words = set(tracker_name.split())
                    req_words = set(req_name.split())
                    overlap = len(tracker_words & req_words)
                    if overlap > 1:
                        score += overlap * 0.5

            if score > best_score and score >= 3:  # Minimum threshold
                best_score = score
                best_match = req_row

    if best_match is not None:
        matches.append({
            'tracker_idx': idx,
            'doc_number': best_match['Doc_Number'],
            'tracker_file': tracker_row['Filename'][:60],
            'tracker_category': tracker_row['Category'][:50],
            'req_name': best_match['document_name'],
            'req_category': best_match['category'],
            'confidence': best_score
        })
        matched_doc_numbers.add(best_match['Doc_Number'])
    else:
        unmatched_tracker.append({
            'filename': tracker_row['Filename'],
            'category': tracker_row['Category'],
            'appendix': tracker_row['Appendix_Number']
        })

# Find unmatched requirements
for _, req_row in req_df.iterrows():
    if req_row['Doc_Number'] not in matched_doc_numbers:
        unmatched_requirements.append({
            'doc_number': req_row['Doc_Number'],
            'doc_name': req_row['document_name'],
            'category': req_row['category'],
            'notes': req_row['notes'] if pd.notna(req_row['notes']) else ''
        })

print(f"✅ Matched {len(matches)} documents")
print(f"⚠️  {len(unmatched_tracker)} tracker documents without requirement match")
print(f"❌ {len(unmatched_requirements)} required documents not found in tracker")
print()

# Show sample matches for verification
print("=" * 100)
print("📋 HIGH CONFIDENCE MATCHES (for verification):")
print("=" * 100)
matches_df = pd.DataFrame(matches)
if len(matches_df) > 0:
    # Show high confidence matches
    high_conf = matches_df[matches_df['confidence'] >= 8].head(20)
    for _, match in high_conf.iterrows():
        print(f"Doc {match['doc_number']}: {match['tracker_file']}")
        print(f"         → {match['req_name']}")
        print(f"         Category: {match['tracker_category']} (conf: {match['confidence']:.1f})")
        print()

# Show sample low confidence matches (may need review)
print("=" * 100)
print("⚠️  LOW CONFIDENCE MATCHES (need manual verification):")
print("=" * 100)
low_conf = matches_df[matches_df['confidence'] < 8].head(15)
for _, match in low_conf.iterrows():
    print(f"Doc {match['doc_number']}: {match['tracker_file']}")
    print(f"         → Maybe: {match['req_name']}")
    print(f"         Confidence: {match['confidence']:.1f}")
    print()

# Save reports
print("💾 Saving reports...")

# Matched documents
matches_df.to_csv('reports/matched_requirements.csv', index=False)
print(f"   ✅ Matched documents: reports/matched_requirements.csv")

# Unmatched tracker docs
if len(unmatched_tracker) > 0:
    pd.DataFrame(unmatched_tracker).to_csv('reports/unmatched_tracker_docs.csv', index=False)
    print(f"   ⚠️  Unmatched tracker docs: reports/unmatched_tracker_docs.csv ({len(unmatched_tracker)} docs)")

# Missing requirements
if len(unmatched_requirements) > 0:
    pd.DataFrame(unmatched_requirements).to_csv('reports/missing_required_docs.csv', index=False)
    print(f"   ❌ Missing required docs: reports/missing_required_docs.csv ({len(unmatched_requirements)} docs)")

print()
print("=" * 100)
print("SUMMARY:")
print(f"  ✅ {len(matches)} documents matched to requirements")
print(f"  ⚠️  {len(unmatched_tracker)} documents in tracker without requirement match (may not be closeout deliverables)")
print(f"  ❌ {len(unmatched_requirements)} required documents missing from tracker")
print()
print("👉 Review the CSV files in reports/ directory")
print("👉 Check matched_requirements.csv for accuracy before applying Doc_Number to tracker")
print()
