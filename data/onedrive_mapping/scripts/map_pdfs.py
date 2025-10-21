#!/usr/bin/env python3
"""
Map OneDrive PDFs to requirements tracker CSV entries.
Creates a comprehensive mapping of all PDFs found in OneDrive and their relationship to the CSV.
"""

import csv
import os
from pathlib import Path
from collections import defaultdict
import json

# Paths
ONEDRIVE_BASE = "/Users/z/Library/CloudStorage/OneDrive-WashingtonStateDepartmentofTransportation"
CSV_PATH = "/Users/z/Desktop/git/montlake-closeout/data/requirements_tracker.csv"
OUTPUT_JSON = "/Users/z/Desktop/git/montlake-closeout/data/pdf_mapping.json"
OUTPUT_TXT = "/Users/z/Desktop/git/montlake-closeout/data/pdf_mapping.txt"

def find_all_pdfs(base_path):
    """Find all PDF files in the OneDrive directory."""
    print(f"Scanning for PDFs in {base_path}...")
    pdfs = []
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.lower().endswith('.pdf'):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, base_path)
                pdfs.append({
                    'filename': file,
                    'full_path': full_path,
                    'relative_path': rel_path,
                    'directory': os.path.dirname(rel_path)
                })
    print(f"Found {len(pdfs)} PDFs")
    return pdfs

def parse_csv(csv_path):
    """Parse the requirements tracker CSV."""
    print(f"Parsing CSV: {csv_path}...")
    entries = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            entries.append({
                'doc_number': row.get('Doc_Number', ''),
                'document_name': row.get('Document_Name', ''),
                'full_name': row.get('Full_Name', ''),
                'category': row.get('Category', ''),
                'document_type': row.get('Document_Type', ''),
                'contract_section': row.get('Contract_Section', ''),
                'review_status': row.get('Review_Status', ''),
                'notes': row.get('Notes', ''),
                'files_count': row.get('Files_Count', ''),
                'representative_file': row.get('Representative_File', ''),
                'file_path': row.get('File_Path', '')
            })
    print(f"Parsed {len(entries)} CSV entries")
    return entries

def create_mapping(pdfs, csv_entries):
    """Create mapping between PDFs and CSV entries."""
    print("Creating mapping...")

    # Index PDFs by filename for quick lookup
    pdfs_by_filename = defaultdict(list)
    for pdf in pdfs:
        pdfs_by_filename[pdf['filename']].append(pdf)

    # Track which PDFs are referenced in CSV
    referenced_pdfs = set()

    # Mapping structure
    mapping = {
        'summary': {
            'total_pdfs': len(pdfs),
            'total_csv_entries': len(csv_entries),
            'csv_entries_with_files': 0,
            'csv_entries_without_files': 0,
            'unique_referenced_pdfs': 0,
            'unreferenced_pdfs': 0
        },
        'csv_to_pdf': [],
        'unreferenced_pdfs': []
    }

    # Map CSV entries to PDFs
    for entry in csv_entries:
        rep_file = entry['representative_file']
        file_path = entry['file_path']

        csv_entry = {
            'doc_number': entry['doc_number'],
            'document_name': entry['document_name'],
            'full_name': entry['full_name'],
            'category': entry['category'],
            'files_count': entry['files_count'],
            'representative_file': rep_file,
            'file_path': file_path,
            'pdf_matches': []
        }

        if rep_file:
            mapping['summary']['csv_entries_with_files'] += 1
            # Find matching PDFs
            if rep_file in pdfs_by_filename:
                for pdf in pdfs_by_filename[rep_file]:
                    csv_entry['pdf_matches'].append({
                        'full_path': pdf['full_path'],
                        'relative_path': pdf['relative_path'],
                        'matches_csv_path': pdf['full_path'] == file_path
                    })
                    referenced_pdfs.add(pdf['full_path'])
        else:
            mapping['summary']['csv_entries_without_files'] += 1

        mapping['csv_to_pdf'].append(csv_entry)

    # Find unreferenced PDFs
    for pdf in pdfs:
        if pdf['full_path'] not in referenced_pdfs:
            mapping['unreferenced_pdfs'].append({
                'filename': pdf['filename'],
                'relative_path': pdf['relative_path'],
                'full_path': pdf['full_path']
            })

    mapping['summary']['unique_referenced_pdfs'] = len(referenced_pdfs)
    mapping['summary']['unreferenced_pdfs'] = len(mapping['unreferenced_pdfs'])

    return mapping

def save_mapping(mapping, json_path, txt_path):
    """Save mapping to JSON and human-readable text files."""
    print(f"Saving mapping to {json_path} and {txt_path}...")

    # Save JSON
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)

    # Save human-readable text
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("PDF MAPPING SUMMARY\n")
        f.write("=" * 80 + "\n\n")

        summary = mapping['summary']
        f.write(f"Total PDFs in OneDrive:           {summary['total_pdfs']:,}\n")
        f.write(f"Total CSV entries:                {summary['total_csv_entries']:,}\n")
        f.write(f"CSV entries with files:           {summary['csv_entries_with_files']:,}\n")
        f.write(f"CSV entries without files:        {summary['csv_entries_without_files']:,}\n")
        f.write(f"Unique PDFs referenced in CSV:    {summary['unique_referenced_pdfs']:,}\n")
        f.write(f"Unreferenced PDFs:                {summary['unreferenced_pdfs']:,}\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("CSV ENTRIES AND THEIR PDF MATCHES\n")
        f.write("=" * 80 + "\n\n")

        for entry in mapping['csv_to_pdf']:
            f.write(f"Doc #{entry['doc_number']}: {entry['document_name']}\n")
            if entry['full_name']:
                f.write(f"  Full Name: {entry['full_name']}\n")
            f.write(f"  Category: {entry['category']}\n")
            f.write(f"  Files Count: {entry['files_count']}\n")
            f.write(f"  Representative File: {entry['representative_file']}\n")

            if entry['pdf_matches']:
                f.write(f"  PDF Matches: {len(entry['pdf_matches'])}\n")
                for match in entry['pdf_matches']:
                    status = "✓ PATH MATCH" if match['matches_csv_path'] else "⚠ PATH DIFFERS"
                    f.write(f"    [{status}] {match['relative_path']}\n")
            else:
                if entry['representative_file']:
                    f.write(f"  ⚠ NO PDF FOUND\n")
                else:
                    f.write(f"  (No file specified)\n")
            f.write("\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write(f"UNREFERENCED PDFs ({len(mapping['unreferenced_pdfs'])})\n")
        f.write("=" * 80 + "\n\n")

        # Group unreferenced PDFs by directory
        by_dir = defaultdict(list)
        for pdf in mapping['unreferenced_pdfs']:
            directory = os.path.dirname(pdf['relative_path'])
            by_dir[directory].append(pdf['filename'])

        for directory in sorted(by_dir.keys()):
            f.write(f"\n{directory}/\n")
            for filename in sorted(by_dir[directory]):
                f.write(f"  - {filename}\n")

def main():
    """Main function."""
    print("\nStarting PDF mapping process...\n")

    # Find all PDFs
    pdfs = find_all_pdfs(ONEDRIVE_BASE)

    # Parse CSV
    csv_entries = parse_csv(CSV_PATH)

    # Create mapping
    mapping = create_mapping(pdfs, csv_entries)

    # Save results
    save_mapping(mapping, OUTPUT_JSON, OUTPUT_TXT)

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total PDFs found:             {mapping['summary']['total_pdfs']:,}")
    print(f"CSV entries:                  {mapping['summary']['total_csv_entries']:,}")
    print(f"PDFs referenced in CSV:       {mapping['summary']['unique_referenced_pdfs']:,}")
    print(f"PDFs not referenced:          {mapping['summary']['unreferenced_pdfs']:,}")
    print(f"\nResults saved to:")
    print(f"  - {OUTPUT_JSON}")
    print(f"  - {OUTPUT_TXT}")
    print("\nDone!")

if __name__ == '__main__':
    main()
