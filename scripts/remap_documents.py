#!/usr/bin/env python3
"""
Improved Document Mapping Script
Maps documents in documents_tracker.csv to OneDrive files with better accuracy.
"""

import csv
import os
import re
from difflib import SequenceMatcher

# Paths
ONEDRIVE_BASE = "/Users/z/Library/CloudStorage/OneDrive-WashingtonStateDepartmentofTransportation"
APPENDICES_DIR = os.path.join(ONEDRIVE_BASE, "TheBRIDGE - Montlake - Contract Documents/Appendices")
CSV_PATH = "data/documents_tracker.csv"
OUTPUT_CSV = "data/documents_tracker_REMAPPED.csv"
REPORT_TXT = "data/remapping_report.txt"

# Load complete APPENDIX_DATA dictionary from the original mapping script
print("📚 Loading appendix mapping data...")
with open('data/onedrive_mapping/scripts/complete_appendix_mapping_ALL.py', 'r') as f:
    content = f.read()
    # Extract the APPENDIX_DATA dictionary definition
    start = content.find('APPENDIX_DATA = {')
    end = content.find('\n}', start) + 2
    appendix_code = content[start:end]
    # Execute it to create the APPENDIX_DATA variable
    exec(appendix_code)
    print(f"✅ Loaded {len(APPENDIX_DATA)} appendix mappings\n")

def similarity_ratio(a, b):
    """Calculate similarity ratio between two strings."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def extract_volume_number(doc_name):
    """Extract volume number from document names like 'Volume 01' or 'As-Built Plans Volume 14a'."""
    # Match patterns like "Volume 01", "Volume 14a", etc.
    match = re.search(r'[Vv]olume\s+(\d+[a-z]?)', doc_name)
    if match:
        return match.group(1).lower()  # Return '01', '14a', etc.
    return None

def match_document_to_appendix_improved(doc_name, full_name, category):
    """
    Improved matching logic with multiple strategies:
    1. Exact match (case-insensitive)
    2. Volume number extraction for as-built plans
    3. High-threshold fuzzy matching
    4. Word-based matching
    """

    # Create list of search terms
    search_terms = []
    if full_name and full_name.strip():
        search_terms.append(full_name.strip())
    if doc_name and doc_name.strip() and doc_name != full_name:
        search_terms.append(doc_name.strip())

    if not search_terms:
        return None, 0, "No search terms"

    # Strategy 1: Exact match
    for search_term in search_terms:
        for (app_category, app_id), app_doc_name in APPENDIX_DATA.items():
            if app_category != category:
                continue
            if search_term.lower().strip() == app_doc_name.lower().strip():
                return app_id, 100, f"Exact match: '{search_term}' == '{app_doc_name}'"

    # Strategy 2: Volume number matching for As-Built plans
    if 'as-built' in doc_name.lower() or 'volume' in doc_name.lower():
        vol_num = extract_volume_number(doc_name)
        if vol_num:
            for (app_category, app_id), app_doc_name in APPENDIX_DATA.items():
                if app_category != category:
                    continue
                app_vol_num = extract_volume_number(app_doc_name)
                if app_vol_num == vol_num:
                    return app_id, 95, f"Volume match: {vol_num}"

    # Strategy 3: High-threshold fuzzy matching
    best_match = None
    best_score = 0
    best_reason = ""

    for search_term in search_terms:
        for (app_category, app_id), app_doc_name in APPENDIX_DATA.items():
            if app_category != category:
                continue

            # Calculate similarity
            ratio = similarity_ratio(search_term, app_doc_name)
            score = int(ratio * 100)

            # Only consider matches with 70%+ similarity
            if score > best_score and score >= 70:
                best_score = score
                best_match = app_id
                best_reason = f"Fuzzy match ({score}%): '{search_term}' ≈ '{app_doc_name}'"

    return best_match, best_score, best_reason

def find_pdf_in_nested_structure(category, appendix_id):
    """
    Find PDF file handling nested folder structures.
    Improved to handle folders with full names like "Appendix A4.1 - Description"
    """
    category_path = os.path.join(APPENDICES_DIR, category)

    if not os.path.exists(category_path):
        return None

    # First, try direct match (for simple appendices like D1, B14, etc.)
    simple_folder = os.path.join(category_path, f"Appendix {appendix_id}")
    if os.path.exists(simple_folder) and os.path.isdir(simple_folder):
        for item in os.listdir(simple_folder):
            if item.endswith('.pdf') and not item.startswith('.'):
                return os.path.join(simple_folder, item)

    # For nested appendices (contains dots), build path progressively
    if '.' in appendix_id:
        parts = appendix_id.split('.')
        current_path = os.path.join(category_path, f"Appendix {parts[0]}")

        if not os.path.exists(current_path):
            return None

        # Navigate through nested folders
        for i in range(1, len(parts)):
            cumulative_id = '.'.join(parts[:i+1])
            possible_names = [
                f"Appendix {cumulative_id}",
                cumulative_id,
            ]

            found_next = False
            for name in possible_names:
                next_path = os.path.join(current_path, name)
                if os.path.exists(next_path):
                    current_path = next_path
                    found_next = True
                    break

            # NEW: Also try folder names with descriptions like "Appendix A4.1 - Description"
            if not found_next and os.path.isdir(current_path):
                for item in os.listdir(current_path):
                    if item.startswith(f"Appendix {cumulative_id}"):
                        next_path = os.path.join(current_path, item)
                        if os.path.isdir(next_path):
                            current_path = next_path
                            found_next = True
                            break

            if not found_next:
                break

        # Search for PDF in the final folder
        if os.path.exists(current_path) and os.path.isdir(current_path):
            for item in os.listdir(current_path):
                if item.endswith('.pdf') and not item.startswith('.'):
                    return os.path.join(current_path, item)

    return None

def process_csv():
    """Process CSV and update with improved appendix file paths."""
    print("📊 Loading documents tracker CSV...")

    docs = []
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            docs.append(row)

    print(f"✅ Loaded {len(docs)} documents\n")

    stats = {
        'total_appendices': 0,
        'matched': 0,
        'file_found': 0,
        'file_not_found': 0,
        'no_match': 0,
        'low_confidence': 0
    }

    report_lines = []
    report_lines.append("=" * 120)
    report_lines.append("IMPROVED DOCUMENT MAPPING REPORT")
    report_lines.append("=" * 120 + "\n")

    # Track what we're updating
    updates = []

    for doc in docs:
        contract_section = doc.get('Contract_Section', '')
        category = doc.get('Category', '').strip()
        doc_name = doc.get('Document_Name', '')
        full_name = doc.get('Full_Name', '').strip()
        doc_number = doc.get('Doc_Number', '')
        doc_type = doc.get('Document_Type', '')

        # Only process appendices (Document_Type == 'Appendix')
        if doc_type != 'Appendix' or not category:
            continue

        stats['total_appendices'] += 1

        # Try to match to appendix
        appendix_id, confidence, reason = match_document_to_appendix_improved(doc_name, full_name, category)

        if appendix_id:
            stats['matched'] += 1

            # Try to find the file
            pdf_path = find_pdf_in_nested_structure(category, appendix_id)

            if pdf_path:
                filename = os.path.basename(pdf_path)

                # Store old values for comparison
                old_rep_file = doc.get('Representative_File', '')
                old_file_path = doc.get('File_Path', '')

                # Update the document
                doc['Representative_File'] = filename
                doc['File_Path'] = pdf_path
                doc['Files_Count'] = '1'

                stats['file_found'] += 1

                # Track changes
                changed = (old_rep_file != filename or old_file_path != pdf_path)
                status = "✓ UPDATED" if changed else "✓ Confirmed"

                updates.append({
                    'doc_number': doc_number,
                    'doc_name': doc_name,
                    'appendix_id': appendix_id,
                    'filename': filename,
                    'confidence': confidence,
                    'reason': reason,
                    'status': status,
                    'old_file': old_rep_file,
                    'new_file': filename
                })

                report_lines.append(f"{status} Doc #{doc_number}: {doc_name}")
                report_lines.append(f"  → Appendix {appendix_id} ({confidence}% confidence)")
                report_lines.append(f"  → File: {filename}")
                report_lines.append(f"  → Reason: {reason}")
                if changed and old_rep_file:
                    report_lines.append(f"  → Changed from: {old_rep_file}")
                report_lines.append("")

                print(f"{status} Doc #{doc_number}: {doc_name} → {appendix_id} ({confidence}%)")

                if confidence < 80:
                    stats['low_confidence'] += 1

            else:
                stats['file_not_found'] += 1
                report_lines.append(f"⚠ MATCHED BUT NO FILE: Doc #{doc_number}: {doc_name}")
                report_lines.append(f"  → Appendix {appendix_id} ({confidence}% confidence)")
                report_lines.append(f"  → File not found in OneDrive structure")
                report_lines.append("")
                print(f"⚠ Doc #{doc_number}: Matched to {appendix_id} but file not found")
        else:
            stats['no_match'] += 1
            report_lines.append(f"✗ NO MATCH: Doc #{doc_number}: {doc_name}")
            report_lines.append(f"  → Category: {category}")
            report_lines.append("")
            print(f"✗ Doc #{doc_number}: {doc_name} - No match found")

    # Generate summary
    report_lines.append("\n" + "=" * 120)
    report_lines.append("SUMMARY")
    report_lines.append("=" * 120)
    report_lines.append(f"Total appendices processed:     {stats['total_appendices']}")
    report_lines.append(f"Successfully matched:           {stats['matched']}")
    report_lines.append(f"  └─ Files found:               {stats['file_found']}")
    report_lines.append(f"  └─ Files not found:           {stats['file_not_found']}")
    report_lines.append(f"  └─ Low confidence matches:    {stats['low_confidence']}")
    report_lines.append(f"No match found:                 {stats['no_match']}")
    report_lines.append("")

    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    for line in report_lines[-8:]:
        print(line)

    # Save updated CSV
    print(f"\n💾 Saving updated CSV to {OUTPUT_CSV}...")
    with open(OUTPUT_CSV, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(docs)

    # Save report
    print(f"📄 Saving detailed report to {REPORT_TXT}...")
    with open(REPORT_TXT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))

    print("\n✅ Done! Review the report before applying changes.")
    print(f"   Report: {REPORT_TXT}")
    print(f"   Output: {OUTPUT_CSV}")

if __name__ == '__main__':
    process_csv()
