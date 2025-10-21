#!/usr/bin/env python3
"""
Map OneDrive files to CSV by using the Category structure.
"""

import csv
import os
from pathlib import Path
from collections import defaultdict
import json

# Paths
ONEDRIVE_BASE = "/Users/z/Library/CloudStorage/OneDrive-WashingtonStateDepartmentofTransportation"
APPENDICES_DIR = os.path.join(ONEDRIVE_BASE, "TheBRIDGE - Montlake - Contract Documents/Appendices")
CHANGE_MGMT_DIR = os.path.join(ONEDRIVE_BASE, "TheBRIDGE - Montlake - Change Management  Documents")
CONTRACT_DOCS_DIR = os.path.join(ONEDRIVE_BASE, "TheBRIDGE - Montlake - Contract Documents")

CSV_PATH = "/Users/z/Desktop/git/montlake-closeout/data/requirements_tracker.csv"
OUTPUT_CSV = "/Users/z/Desktop/git/montlake-closeout/data/requirements_tracker_updated.csv"
REPORT_TXT = "/Users/z/Desktop/git/montlake-closeout/data/mapping_report.txt"

def scan_folder_recursively(folder_path, max_depth=5):
    """Scan a folder recursively and return all files and subdirectories."""
    items = {
        'files': [],
        'folders': [],
        'files_by_name': {},
        'folders_by_name': {}
    }

    if not os.path.exists(folder_path):
        return items

    def scan(path, depth=0):
        if depth > max_depth:
            return

        try:
            entries = os.listdir(path)
        except PermissionError:
            return

        for entry in entries:
            if entry.startswith('.'):
                continue

            full_path = os.path.join(path, entry)

            if os.path.isdir(full_path):
                folder_info = {
                    'name': entry,
                    'full_path': full_path,
                    'relative_path': os.path.relpath(full_path, folder_path),
                    'depth': depth
                }
                items['folders'].append(folder_info)
                items['folders_by_name'][entry] = folder_info
                scan(full_path, depth + 1)
            else:
                file_info = {
                    'name': entry,
                    'full_path': full_path,
                    'relative_path': os.path.relpath(full_path, folder_path),
                    'folder': os.path.dirname(full_path)
                }
                items['files'].append(file_info)
                items['files_by_name'][entry] = file_info

    scan(folder_path)
    return items

def find_files_in_category(category, doc_name, full_name, appendices_dir):
    """Find files for a document within its category folder."""
    if not category:
        return None

    category_path = os.path.join(appendices_dir, category)

    if not os.path.exists(category_path):
        return None

    # Scan the category folder
    items = scan_folder_recursively(category_path)

    # Look for files or folders matching the document name or full name
    search_terms = []
    if full_name:
        search_terms.append(full_name)
    if doc_name and doc_name != full_name:
        search_terms.append(doc_name)

    matches = {
        'files': [],
        'folders': []
    }

    # Check for exact filename matches (including .pdf extension)
    for term in search_terms:
        pdf_name = term if term.endswith('.pdf') else f"{term}.pdf"

        # Check if file exists with this name
        for file_info in items['files']:
            if file_info['name'].lower() == pdf_name.lower():
                matches['files'].append(file_info)

    # Check for folder matches
    for term in search_terms:
        for folder_info in items['folders']:
            if folder_info['name'].lower() == term.lower():
                matches['folders'].append(folder_info)

    # If we found a folder match, scan it for PDFs
    if matches['folders'] and not matches['files']:
        folder_path = matches['folders'][0]['full_path']
        folder_items = scan_folder_recursively(folder_path, max_depth=3)
        matches['files'] = [f for f in folder_items['files'] if f['name'].lower().endswith('.pdf')]

    return matches if (matches['files'] or matches['folders']) else None

def load_csv_and_map(csv_path, appendices_dir):
    """Load CSV and map files."""
    print(f"Loading CSV: {csv_path}")

    docs = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            docs.append(row)

    print(f"  Loaded {len(docs)} documents")

    # Process documents
    updates_made = 0
    report = []

    for doc in docs:
        contract_section = doc.get('Contract_Section', '')
        rep_file = doc.get('Representative_File', '').strip()
        category = doc.get('Category', '').strip()
        doc_name = doc.get('Document_Name', '')
        full_name = doc.get('Full_Name', '').strip()
        doc_number = doc.get('Doc_Number', '')

        # Only process contract documents without files
        is_contract_doc = any(contract_section.startswith(f"{i}.") for i in range(1, 9))

        if not is_contract_doc or rep_file or not category:
            continue

        # Try to find files in the category
        matches = find_files_in_category(category, doc_name, full_name, appendices_dir)

        if matches and matches['files']:
            # Found files!
            pdf_files = matches['files']
            first_pdf = pdf_files[0]

            doc['Files_Count'] = str(len(pdf_files))
            doc['Representative_File'] = first_pdf['name']
            doc['File_Path'] = first_pdf['full_path']

            updates_made += 1

            report.append({
                'doc_number': doc_number,
                'document_name': doc_name,
                'category': category,
                'status': 'FOUND',
                'files_count': len(pdf_files),
                'representative_file': first_pdf['name'],
                'path': first_pdf['relative_path']
            })
        else:
            report.append({
                'doc_number': doc_number,
                'document_name': doc_name,
                'category': category,
                'status': 'NOT_FOUND',
                'files_count': 0,
                'representative_file': '',
                'path': ''
            })

    print(f"  Updates made: {updates_made}")

    return docs, fieldnames, report, updates_made

def save_results(docs, fieldnames, report, output_csv, report_txt):
    """Save updated CSV and report."""
    print(f"\nSaving results...")

    # Save CSV
    with open(output_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(docs)
    print(f"  ✓ CSV saved: {output_csv}")

    # Save report
    with open(report_txt, 'w', encoding='utf-8') as f:
        f.write("=" * 100 + "\n")
        f.write("MAPPING REPORT\n")
        f.write("=" * 100 + "\n\n")

        found_items = [r for r in report if r['status'] == 'FOUND']
        not_found_items = [r for r in report if r['status'] == 'NOT_FOUND']

        f.write(f"Found: {len(found_items)}\n")
        f.write(f"Not Found: {len(not_found_items)}\n\n")

        if found_items:
            f.write("=" * 100 + "\n")
            f.write("FOUND\n")
            f.write("=" * 100 + "\n\n")
            for item in found_items:
                f.write(f"[✓] Doc #{item['doc_number']}: {item['document_name']}\n")
                f.write(f"    Category: {item['category']}\n")
                f.write(f"    Files: {item['files_count']}\n")
                f.write(f"    Representative: {item['representative_file']}\n")
                f.write(f"    Path: {item['path']}\n\n")

        if not_found_items:
            f.write("=" * 100 + "\n")
            f.write("NOT FOUND\n")
            f.write("=" * 100 + "\n\n")
            for item in not_found_items:
                f.write(f"[✗] Doc #{item['doc_number']}: {item['document_name']}\n")
                f.write(f"    Category: {item['category']}\n\n")

    print(f"  ✓ Report saved: {report_txt}")

def main():
    """Main function."""
    print("\n" + "=" * 100)
    print("MAP FILES BY CATEGORY")
    print("=" * 100 + "\n")

    # Load and map
    docs, fieldnames, report, updates_made = load_csv_and_map(CSV_PATH, APPENDICES_DIR)

    # Save results
    save_results(docs, fieldnames, report, OUTPUT_CSV, REPORT_TXT)

    print("\n" + "=" * 100)
    print(f"COMPLETE! Made {updates_made} updates")
    print("=" * 100 + "\n")

if __name__ == '__main__':
    main()
