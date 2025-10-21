#!/usr/bin/env python3
"""
Find PDFs in OneDrive for documents that don't have files specified yet.
Update the CSV with found matches.
"""

import csv
import os
from pathlib import Path
from collections import defaultdict
import json
import re
from difflib import SequenceMatcher

# Paths
ONEDRIVE_BASE = "/Users/z/Library/CloudStorage/OneDrive-WashingtonStateDepartmentofTransportation"
CSV_PATH = "/Users/z/Desktop/git/montlake-closeout/data/requirements_tracker.csv"
OUTPUT_CSV = "/Users/z/Desktop/git/montlake-closeout/data/requirements_tracker_updated.csv"
REPORT_TXT = "/Users/z/Desktop/git/montlake-closeout/data/missing_files_found.txt"
REPORT_JSON = "/Users/z/Desktop/git/montlake-closeout/data/missing_files_found.json"

def find_all_pdfs(base_path):
    """Find all PDF files in the OneDrive directory with metadata."""
    print(f"Scanning for PDFs in {base_path}...")
    pdfs = []

    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.lower().endswith('.pdf'):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, base_path)

                pdfs.append({
                    'filename': file,
                    'filename_no_ext': os.path.splitext(file)[0],
                    'full_path': full_path,
                    'relative_path': rel_path,
                    'directory': os.path.dirname(rel_path),
                    'filename_lower': file.lower(),
                    'filename_no_ext_lower': os.path.splitext(file)[0].lower()
                })

    print(f"Found {len(pdfs)} PDFs")
    return pdfs

def normalize_string(s):
    """Normalize string for comparison."""
    if not s:
        return ""
    # Convert to lowercase, remove extra spaces
    s = s.lower().strip()
    # Remove special characters but keep spaces and alphanumeric
    s = re.sub(r'[^\w\s-]', '', s)
    # Collapse multiple spaces
    s = re.sub(r'\s+', ' ', s)
    return s

def similarity_score(s1, s2):
    """Calculate similarity between two strings."""
    return SequenceMatcher(None, normalize_string(s1), normalize_string(s2)).ratio()

def search_for_matches(doc, pdfs, threshold=0.7):
    """
    Search for PDF files that might match this document.
    Returns list of matches sorted by confidence score.
    """
    matches = []

    # Get search terms from document
    doc_name = doc.get('document_name', '')
    full_name = doc.get('full_name', '')
    doc_number = doc.get('doc_number', '')

    search_terms = []
    if doc_name:
        search_terms.append(('document_name', doc_name))
    if full_name and full_name != doc_name:
        search_terms.append(('full_name', full_name))

    # Search through all PDFs
    for pdf in pdfs:
        best_score = 0
        best_match_type = None

        # Check filename without extension
        for term_type, term in search_terms:
            score = similarity_score(term, pdf['filename_no_ext'])
            if score > best_score:
                best_score = score
                best_match_type = f"{term_type}_to_filename"

        # Check if doc number appears in filename
        if doc_number:
            if doc_number.lower() in pdf['filename_lower']:
                # Boost score if doc number found
                best_score = max(best_score, 0.6)
                if not best_match_type:
                    best_match_type = "doc_number_in_filename"

        # If score is above threshold, add to matches
        if best_score >= threshold:
            matches.append({
                'pdf': pdf,
                'score': best_score,
                'match_type': best_match_type
            })

    # Sort by score (highest first)
    matches.sort(key=lambda x: x['score'], reverse=True)

    return matches

def parse_csv(csv_path):
    """Parse the requirements tracker CSV."""
    print(f"Parsing CSV: {csv_path}...")

    all_docs = []
    missing_files = []

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames

        for row in reader:
            all_docs.append(row)

            # Check if this is a contract document and missing a file
            contract_section = row.get('Contract_Section', '')
            rep_file = row.get('Representative_File', '').strip()

            # Only process contract documents (sections 1-8)
            is_contract_doc = any(contract_section.startswith(f"{i}.") for i in range(1, 9))

            if is_contract_doc and not rep_file:
                missing_files.append(row)

    print(f"Total documents: {len(all_docs)}")
    print(f"Contract documents missing files: {len(missing_files)}")

    return all_docs, missing_files, fieldnames

def find_and_update(all_docs, missing_files, pdfs, fieldnames):
    """Find matches for missing files and prepare updated CSV."""
    print(f"\nSearching for matches...")

    results = {
        'found_high_confidence': [],  # score >= 0.9
        'found_medium_confidence': [],  # 0.7 <= score < 0.9
        'not_found': []  # no matches above threshold
    }

    # Create a mapping of doc_number to index for quick updates
    doc_lookup = {doc['Doc_Number']: i for i, doc in enumerate(all_docs)}

    for doc in missing_files:
        matches = search_for_matches(doc, pdfs, threshold=0.7)

        doc_info = {
            'doc_number': doc['Doc_Number'],
            'document_name': doc['Document_Name'],
            'full_name': doc['Full_Name'],
            'category': doc['Category'],
            'contract_section': doc['Contract_Section'],
            'matches': []
        }

        if matches:
            # Take top 3 matches
            for match in matches[:3]:
                doc_info['matches'].append({
                    'filename': match['pdf']['filename'],
                    'relative_path': match['pdf']['relative_path'],
                    'full_path': match['pdf']['full_path'],
                    'score': match['score'],
                    'match_type': match['match_type']
                })

            # Categorize by confidence
            top_score = matches[0]['score']
            if top_score >= 0.9:
                results['found_high_confidence'].append(doc_info)
            else:
                results['found_medium_confidence'].append(doc_info)

            # Update the CSV data with best match
            best_match = matches[0]['pdf']
            idx = doc_lookup[doc['Doc_Number']]
            all_docs[idx]['Representative_File'] = best_match['filename']
            all_docs[idx]['File_Path'] = best_match['full_path']
            all_docs[idx]['Files_Count'] = '1'  # At least 1 found

        else:
            results['not_found'].append(doc_info)

    print(f"  High confidence matches (>=90%): {len(results['found_high_confidence'])}")
    print(f"  Medium confidence matches (70-89%): {len(results['found_medium_confidence'])}")
    print(f"  No matches found: {len(results['not_found'])}")

    return all_docs, results

def save_results(updated_docs, results, fieldnames, csv_path, txt_path, json_path):
    """Save updated CSV and reports."""
    print(f"\nSaving results...")

    # Save updated CSV
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(updated_docs)
    print(f"  ✓ Updated CSV: {csv_path}")

    # Save JSON report
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"  ✓ JSON report: {json_path}")

    # Save text report
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write("=" * 100 + "\n")
        f.write("MISSING FILES SEARCH RESULTS\n")
        f.write("=" * 100 + "\n\n")

        f.write("SUMMARY\n")
        f.write("-" * 100 + "\n")
        f.write(f"High confidence matches (>=90%):      {len(results['found_high_confidence'])}\n")
        f.write(f"Medium confidence matches (70-89%):   {len(results['found_medium_confidence'])}\n")
        f.write(f"No matches found:                     {len(results['not_found'])}\n")
        f.write(f"\n")

        # High confidence matches
        if results['found_high_confidence']:
            f.write("\n" + "=" * 100 + "\n")
            f.write("HIGH CONFIDENCE MATCHES (>=90%)\n")
            f.write("=" * 100 + "\n\n")

            for doc in results['found_high_confidence']:
                f.write(f"Doc #{doc['doc_number']}: {doc['document_name']}\n")
                if doc['full_name']:
                    f.write(f"  Full Name: {doc['full_name']}\n")
                f.write(f"  Section: {doc['contract_section']}\n")
                f.write(f"  Category: {doc['category']}\n")

                if doc['matches']:
                    best = doc['matches'][0]
                    f.write(f"  ✓ MATCH: {best['filename']} ({best['score']:.1%} confidence)\n")
                    f.write(f"    Path: {best['relative_path']}\n")

                    if len(doc['matches']) > 1:
                        f.write(f"  Other possible matches:\n")
                        for alt in doc['matches'][1:]:
                            f.write(f"    - {alt['filename']} ({alt['score']:.1%})\n")
                f.write("\n")

        # Medium confidence matches
        if results['found_medium_confidence']:
            f.write("\n" + "=" * 100 + "\n")
            f.write("MEDIUM CONFIDENCE MATCHES (70-89%)\n")
            f.write("=" * 100 + "\n\n")

            for doc in results['found_medium_confidence']:
                f.write(f"Doc #{doc['doc_number']}: {doc['document_name']}\n")
                if doc['full_name']:
                    f.write(f"  Full Name: {doc['full_name']}\n")
                f.write(f"  Section: {doc['contract_section']}\n")
                f.write(f"  Category: {doc['category']}\n")

                if doc['matches']:
                    for i, match in enumerate(doc['matches']):
                        prefix = "✓ MATCH" if i == 0 else "  Alt"
                        f.write(f"  {prefix}: {match['filename']} ({match['score']:.1%} confidence)\n")
                        if i == 0:
                            f.write(f"    Path: {match['relative_path']}\n")
                f.write("\n")

        # Not found
        if results['not_found']:
            f.write("\n" + "=" * 100 + "\n")
            f.write("NO MATCHES FOUND\n")
            f.write("=" * 100 + "\n\n")

            for doc in results['not_found']:
                f.write(f"Doc #{doc['doc_number']}: {doc['document_name']}\n")
                if doc['full_name']:
                    f.write(f"  Full Name: {doc['full_name']}\n")
                f.write(f"  Section: {doc['contract_section']}\n")
                f.write(f"  Category: {doc['category']}\n")
                f.write("\n")

    print(f"  ✓ Text report: {txt_path}")

def main():
    """Main function."""
    print("\n" + "=" * 100)
    print("FIND MISSING FILES IN ONEDRIVE")
    print("=" * 100 + "\n")

    # Find all PDFs
    pdfs = find_all_pdfs(ONEDRIVE_BASE)

    # Parse CSV
    all_docs, missing_files, fieldnames = parse_csv(CSV_PATH)

    if not missing_files:
        print("\n✓ No missing files found! All contract documents have files specified.")
        return

    # Find matches and update
    updated_docs, results = find_and_update(all_docs, missing_files, pdfs, fieldnames)

    # Save results
    save_results(updated_docs, results, fieldnames, OUTPUT_CSV, REPORT_TXT, REPORT_JSON)

    print("\n" + "=" * 100)
    print("COMPLETE!")
    print("=" * 100)
    print(f"Updated CSV saved to: {OUTPUT_CSV}")
    print(f"Review the matches in: {REPORT_TXT}")
    print("=" * 100 + "\n")

if __name__ == '__main__':
    main()
