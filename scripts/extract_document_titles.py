#!/usr/bin/env python3
"""
Extract actual document titles from PDFs
Adds Document_Title column to tracker so we can see what we're actually reviewing
"""

import pandas as pd
import PyPDF2
import re
from pathlib import Path

def extract_title_from_pdf(pdf_path):
    """
    Extract document title from PDF
    Tries: 1) PDF metadata, 2) First page text
    """
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)

            # Try metadata first
            if pdf_reader.metadata and pdf_reader.metadata.title:
                title = pdf_reader.metadata.title.strip()
                if title and len(title) > 3:
                    return title

            # Try extracting from first page
            if len(pdf_reader.pages) > 0:
                first_page = pdf_reader.pages[0]
                text = first_page.extract_text()

                # Clean up text
                lines = [line.strip() for line in text.split('\n') if line.strip()]

                # Skip common header junk and look for substantial text
                skip_patterns = [
                    r'^SR\s*520',
                    r'^Appendix [A-Z]',
                    r'^Page \d+',
                    r'^\d+$',
                    r'^Washington State',
                    r'^Department of Transportation',
                    r'^Request for Proposal',
                    r'^February.*\d{4}',
                    r'^Montlake'
                ]

                for line in lines:
                    # Skip if too short
                    if len(line) < 5:
                        continue

                    # Skip if matches a header pattern
                    if any(re.match(pattern, line, re.IGNORECASE) for pattern in skip_patterns):
                        continue

                    # This might be the title
                    # Clean it up
                    title = line.strip()

                    # Remove common prefixes
                    title = re.sub(r'^Appendix [A-Z]+[0-9]*\.?\s*[-:]\s*', '', title, flags=re.IGNORECASE)

                    if len(title) > 10:  # Reasonable title length
                        return title

                # If nothing found, return first substantial line
                for line in lines:
                    if len(line) > 10:
                        return line[:200]  # Limit length

        return ""
    except Exception as e:
        print(f"  Error reading {pdf_path}: {str(e)[:50]}")
        return ""

def main():
    print("📄 Extracting Document Titles from PDFs...")
    print()

    # Load tracker
    tracker_df = pd.read_csv('data/contract_documents_complete_tracker.csv', encoding='utf-8-sig')
    print(f"✅ Loaded {len(tracker_df)} documents")

    # Filter to PDFs only (and exclude cover sheets for now)
    pdf_docs = tracker_df[
        (tracker_df['File_Type'] == '.PDF') &
        (~tracker_df['Filename'].str.contains('Cover Sheet', case=False, na=False))
    ].copy()

    print(f"📊 Processing {len(pdf_docs)} non-cover-sheet PDFs")
    print()

    # Add Document_Title column
    tracker_df['Document_Title'] = ''

    # Process in batches with progress
    total = len(pdf_docs)
    processed = 0
    errors = 0

    for idx, row in pdf_docs.iterrows():
        processed += 1

        if processed % 50 == 0:
            print(f"  Progress: {processed}/{total} ({processed/total*100:.1f}%)")

        pdf_path = row['Full_Path']

        # Check if file exists
        if not Path(pdf_path).exists():
            errors += 1
            continue

        # Extract title
        title = extract_title_from_pdf(pdf_path)

        # Store in tracker
        tracker_df.at[idx, 'Document_Title'] = title

    print()
    print(f"✅ Extracted titles from {processed - errors} PDFs")
    print(f"⚠️  {errors} files had errors")
    print()

    # Show sample results
    print("Sample extracted titles:")
    print("=" * 100)
    samples = tracker_df[tracker_df['Document_Title'] != ''].head(20)
    for _, row in samples.iterrows():
        print(f"{row['Filename'][:40]:40} → {row['Document_Title'][:55]}")

    print()

    # Save updated tracker
    # Reorder columns to put Document_Title after Filename
    columns = list(tracker_df.columns)
    columns.remove('Document_Title')
    filename_idx = columns.index('Filename')
    columns.insert(filename_idx + 1, 'Document_Title')
    tracker_df = tracker_df[columns]

    tracker_df.to_csv('data/contract_documents_complete_tracker.csv', index=False)
    print(f"💾 Saved updated tracker with Document_Title column")
    print()

    # Statistics
    has_title = len(tracker_df[tracker_df['Document_Title'] != ''])
    print(f"📊 Documents with titles: {has_title}/{len(tracker_df)}")
    print()

    print("✅ Title extraction complete!")
    print()

if __name__ == "__main__":
    main()
