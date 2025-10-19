#!/usr/bin/env python3
"""
Scan and catalog all appendices from the Montlake project
Creates a comprehensive map for closeout requirement searching
"""

import os
import re
from pathlib import Path
import csv
from datetime import datetime

# Base path to appendices
APPENDICES_PATH = Path("/Users/z/Library/CloudStorage/OneDrive-WashingtonStateDepartmentofTransportation/TheBRIDGE - Montlake - Change Management  Documents/120_RFP Conformed to COs/Appendices")

def extract_appendix_number(path_str):
    """Extract appendix number/ID from path"""
    # Look for patterns like "Appendix A1", "Appendix TF3.B", etc.
    match = re.search(r'Appendix\s+([A-Z]+\d*(?:\.\w+)?)', path_str, re.IGNORECASE)
    if match:
        return match.group(1)
    return ""

def get_file_info(file_path):
    """Get file information"""
    try:
        stat = file_path.stat()
        size_mb = stat.st_size / (1024 * 1024)
        mod_time = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d')
        return size_mb, mod_time
    except:
        return 0, ""

def scan_appendices():
    """Scan all appendices and create inventory"""

    appendix_data = []

    print("🔍 Scanning appendices...")

    # Walk through all directories
    for category_dir in sorted(APPENDICES_PATH.iterdir()):
        if not category_dir.is_dir():
            continue

        category_name = category_dir.name
        print(f"  📁 {category_name}")

        # Count files in this category
        file_count = 0

        # Walk through subdirectories
        for root, dirs, files in os.walk(category_dir):
            root_path = Path(root)

            # Get relative path from category
            rel_path = root_path.relative_to(category_dir)

            for file in sorted(files):
                if file.startswith('.') or file.startswith('~'):
                    continue

                file_path = root_path / file
                ext = file_path.suffix.lower()

                # Only process document files
                if ext not in ['.pdf', '.docx', '.doc', '.xlsx', '.xls']:
                    continue

                file_count += 1

                # Extract appendix number
                appendix_num = extract_appendix_number(str(file_path))

                # Get file info
                size_mb, mod_date = get_file_info(file_path)

                # Store data
                appendix_data.append({
                    'Category': category_name,
                    'Appendix_Number': appendix_num,
                    'Subfolder': str(rel_path) if str(rel_path) != '.' else '',
                    'Filename': file,
                    'File_Type': ext.upper(),
                    'Size_MB': f"{size_mb:.2f}",
                    'Modified_Date': mod_date,
                    'Full_Path': str(file_path)
                })

        print(f"     Found {file_count} files")

    return appendix_data

def create_summary(appendix_data):
    """Create summary statistics"""

    summary = []

    # Group by category
    categories = {}
    for item in appendix_data:
        cat = item['Category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(item)

    summary.append("=" * 80)
    summary.append("MONTLAKE PROJECT APPENDICES SUMMARY")
    summary.append("=" * 80)
    summary.append(f"Total Files: {len(appendix_data)}")
    summary.append(f"Total Categories: {len(categories)}")
    summary.append("")
    summary.append("BY CATEGORY:")
    summary.append("-" * 80)

    for cat in sorted(categories.keys()):
        items = categories[cat]

        # Count file types
        pdf_count = len([i for i in items if i['File_Type'] == '.PDF'])
        docx_count = len([i for i in items if i['File_Type'] in ['.DOCX', '.DOC']])
        excel_count = len([i for i in items if i['File_Type'] in ['.XLSX', '.XLS']])

        # Get unique appendix numbers
        appendix_nums = set([i['Appendix_Number'] for i in items if i['Appendix_Number']])

        summary.append(f"{cat}")
        summary.append(f"  Total Files: {len(items)}")
        if appendix_nums:
            summary.append(f"  Appendices: {', '.join(sorted(appendix_nums))}")
        summary.append(f"  PDFs: {pdf_count} | Word: {docx_count} | Excel: {excel_count}")
        summary.append("")

    return "\n".join(summary)

def main():
    print("📊 Montlake Appendices Scanner")
    print("=" * 80)
    print()

    # Scan appendices
    appendix_data = scan_appendices()

    print()
    print(f"✅ Scanned {len(appendix_data)} files")
    print()

    # Create output directory
    output_dir = Path("/Users/z/Desktop/git/montlake-closeout")
    output_dir.mkdir(exist_ok=True)

    # Write CSV
    csv_file = output_dir / "appendices_inventory.csv"
    print(f"💾 Writing inventory to: {csv_file}")

    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        if appendix_data:
            writer = csv.DictWriter(f, fieldnames=appendix_data[0].keys())
            writer.writeheader()
            writer.writerows(appendix_data)

    # Create summary
    summary = create_summary(appendix_data)

    # Write summary
    summary_file = output_dir / "appendices_summary.txt"
    print(f"📄 Writing summary to: {summary_file}")

    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(summary)

    print()
    print(summary)
    print()
    print("✅ Done!")

if __name__ == "__main__":
    main()
