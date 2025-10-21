#!/usr/bin/env python3
"""
Comprehensively scan OneDrive structure and map to CSV documents.
"""

import csv
import os
from pathlib import Path
from collections import defaultdict
import json

# Paths
ONEDRIVE_BASE = "/Users/z/Library/CloudStorage/OneDrive-WashingtonStateDepartmentofTransportation"
CSV_PATH = "/Users/z/Desktop/git/montlake-closeout/data/requirements_tracker.csv"
OUTPUT_CSV = "/Users/z/Desktop/git/montlake-closeout/data/requirements_tracker_updated.csv"
STRUCTURE_JSON = "/Users/z/Desktop/git/montlake-closeout/data/onedrive_structure.json"

def scan_directory_structure(base_path, max_depth=10):
    """Recursively scan directory structure."""
    print(f"Scanning directory structure: {base_path}")

    structure = {
        'folders': [],
        'files_by_folder': {},
        'all_files': [],
        'all_pdfs': []
    }

    def scan_dir(path, depth=0):
        if depth > max_depth:
            return

        try:
            items = os.listdir(path)
        except PermissionError:
            return

        for item in items:
            if item.startswith('.'):
                continue

            full_path = os.path.join(path, item)
            rel_path = os.path.relpath(full_path, base_path)

            if os.path.isdir(full_path):
                structure['folders'].append({
                    'name': item,
                    'full_path': full_path,
                    'relative_path': rel_path,
                    'depth': depth
                })
                scan_dir(full_path, depth + 1)
            else:
                file_info = {
                    'name': item,
                    'full_path': full_path,
                    'relative_path': rel_path,
                    'folder': os.path.dirname(rel_path),
                    'extension': os.path.splitext(item)[1].lower()
                }

                structure['all_files'].append(file_info)

                folder_key = os.path.dirname(rel_path)
                if folder_key not in structure['files_by_folder']:
                    structure['files_by_folder'][folder_key] = []
                structure['files_by_folder'][folder_key].append(file_info)

                if file_info['extension'] == '.pdf':
                    structure['all_pdfs'].append(file_info)

    scan_dir(base_path)

    print(f"  Found {len(structure['folders'])} folders")
    print(f"  Found {len(structure['all_files'])} files")
    print(f"  Found {len(structure['all_pdfs'])} PDFs")

    return structure

def load_csv(csv_path):
    """Load CSV and return docs and fieldnames."""
    print(f"\nLoading CSV: {csv_path}")

    docs = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            docs.append(row)

    print(f"  Loaded {len(docs)} documents")

    # Count missing files in contract sections
    missing_count = 0
    for doc in docs:
        contract_section = doc.get('Contract_Section', '')
        rep_file = doc.get('Representative_File', '').strip()
        is_contract_doc = any(contract_section.startswith(f"{i}.") for i in range(1, 9))
        if is_contract_doc and not rep_file:
            missing_count += 1

    print(f"  Contract documents missing files: {missing_count}")

    return docs, fieldnames

def map_structure_to_csv(docs, structure):
    """Map OneDrive structure to CSV documents and update missing files."""
    print(f"\nMapping structure to documents...")

    updates_made = 0

    # Create quick lookup for PDFs by filename
    pdfs_by_name = defaultdict(list)
    for pdf in structure['all_pdfs']:
        pdfs_by_name[pdf['name']].append(pdf)

    # Also create lookup by folder name
    folders_by_name = defaultdict(list)
    for folder in structure['folders']:
        folder_name = folder['name']
        folders_by_name[folder_name].append(folder)

    for doc in docs:
        contract_section = doc.get('Contract_Section', '')
        rep_file = doc.get('Representative_File', '').strip()
        doc_name = doc.get('Document_Name', '')
        full_name = doc.get('Full_Name', '')
        category = doc.get('Category', '')

        # Only process contract documents without files
        is_contract_doc = any(contract_section.startswith(f"{i}.") for i in range(1, 9))
        if not is_contract_doc or rep_file:
            continue

        # Strategy 1: Look for folders that match document name or full name
        search_names = []
        if full_name:
            search_names.append(full_name)
        if doc_name and doc_name not in search_names:
            search_names.append(doc_name)

        best_match = None

        # Check for folder matches
        for search_name in search_names:
            if search_name in folders_by_name:
                folder_matches = folders_by_name[search_name]
                if len(folder_matches) > 0:
                    # Found a matching folder - look for PDFs in it
                    folder = folder_matches[0]  # Take first match
                    folder_key = folder['relative_path']

                    if folder_key in structure['files_by_folder']:
                        pdfs_in_folder = [f for f in structure['files_by_folder'][folder_key]
                                         if f['extension'] == '.pdf']

                        if pdfs_in_folder:
                            # Count PDFs and set representative file
                            doc['Files_Count'] = str(len(pdfs_in_folder))
                            # Use first PDF as representative
                            first_pdf = pdfs_in_folder[0]
                            doc['Representative_File'] = first_pdf['name']
                            doc['File_Path'] = first_pdf['full_path']
                            updates_made += 1
                            best_match = first_pdf
                            break

        # Strategy 2: Look for PDFs that match the document name
        if not best_match:
            for search_name in search_names:
                pdf_name = search_name if search_name.endswith('.pdf') else f"{search_name}.pdf"
                if pdf_name in pdfs_by_name:
                    pdf_matches = pdfs_by_name[pdf_name]
                    if len(pdf_matches) > 0:
                        first_pdf = pdf_matches[0]
                        doc['Files_Count'] = str(len(pdf_matches))
                        doc['Representative_File'] = first_pdf['name']
                        doc['File_Path'] = first_pdf['full_path']
                        updates_made += 1
                        best_match = first_pdf
                        break

    print(f"  Updates made: {updates_made}")
    return docs, updates_made

def save_updated_csv(docs, fieldnames, output_path):
    """Save updated CSV."""
    print(f"\nSaving updated CSV to: {output_path}")

    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(docs)

    print(f"  ✓ Saved")

def save_structure(structure, output_path):
    """Save structure to JSON for reference."""
    print(f"\nSaving structure to: {output_path}")

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(structure, f, indent=2, ensure_ascii=False)

    print(f"  ✓ Saved")

def main():
    """Main function."""
    print("\n" + "=" * 100)
    print("SCAN ONEDRIVE AND UPDATE CSV")
    print("=" * 100 + "\n")

    # Scan OneDrive structure
    structure = scan_directory_structure(ONEDRIVE_BASE)

    # Load CSV
    docs, fieldnames = load_csv(CSV_PATH)

    # Map and update
    updated_docs, updates_made = map_structure_to_csv(docs, structure)

    # Save results
    save_updated_csv(updated_docs, fieldnames, OUTPUT_CSV)
    save_structure(structure, STRUCTURE_JSON)

    print("\n" + "=" * 100)
    print(f"COMPLETE! Made {updates_made} updates")
    print("=" * 100 + "\n")

if __name__ == '__main__':
    main()
