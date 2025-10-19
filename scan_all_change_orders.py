#!/usr/bin/env python3
"""
Scan ALL change orders (001-189) and catalog them
Identify executed vs missing COs
"""

import os
from pathlib import Path
import re
from datetime import datetime

# Base path to change orders
CO_PATH = Path("/Users/z/Library/CloudStorage/OneDrive-WashingtonStateDepartmentofTransportation/TheBRIDGE - Montlake - Change Management  Documents/050_Change Orders")

def scan_change_orders():
    """Scan all change order folders and find executed PDFs"""

    print("🔍 Scanning Change Orders 001-189...")
    print()

    change_orders = []

    # Expected range: CO 001 through CO 189
    for co_num in range(1, 190):
        co_id = f"{co_num:03d}"

        # Search for this CO folder
        co_found = False
        co_folder = None
        executed_pdf = None

        # Look through all batch folders
        for batch_folder in sorted(CO_PATH.glob("Change Orders *")):
            # Find folder matching this CO number
            for folder in batch_folder.iterdir():
                if not folder.is_dir():
                    continue

                # Extract CO number from folder name
                match = re.search(rf'^{co_id}_', folder.name)
                if match:
                    co_found = True
                    co_folder = folder

                    # Look for executed PDF
                    executed_folder = co_folder / "Executed CO (Final Docs)"
                    if not executed_folder.exists():
                        # Try alternate naming
                        executed_folder = co_folder / "Executed CO (final docs)"

                    if executed_folder.exists():
                        # Find the -signed.pdf file
                        signed_pdfs = list(executed_folder.glob("*signed*.pdf"))
                        if signed_pdfs:
                            executed_pdf = signed_pdfs[0]

                    break

            if co_found:
                break

        # Record findings
        if co_found:
            if executed_pdf:
                size_mb = executed_pdf.stat().st_size / (1024*1024)
                mod_date = datetime.fromtimestamp(executed_pdf.stat().st_mtime).strftime('%Y-%m-%d')

                change_orders.append({
                    'CO_Number': co_id,
                    'Status': 'EXECUTED',
                    'Filename': executed_pdf.name,
                    'Folder': co_folder.name,
                    'Size_MB': f"{size_mb:.2f}",
                    'Modified_Date': mod_date,
                    'Full_Path': str(executed_pdf),
                    'Notes': ''
                })
            else:
                change_orders.append({
                    'CO_Number': co_id,
                    'Status': 'FOLDER EXISTS - NO EXECUTED PDF',
                    'Filename': '',
                    'Folder': co_folder.name if co_folder else '',
                    'Size_MB': '0.00',
                    'Modified_Date': '',
                    'Full_Path': str(co_folder) if co_folder else '',
                    'Notes': 'Folder exists but no signed/executed PDF found'
                })
        else:
            change_orders.append({
                'CO_Number': co_id,
                'Status': 'MISSING',
                'Filename': '',
                'Folder': '',
                'Size_MB': '0.00',
                'Modified_Date': '',
                'Full_Path': '',
                'Notes': 'No folder found for this CO number'
            })

    return change_orders

def main():
    print("=" * 80)
    print("CHANGE ORDERS COMPREHENSIVE SCAN")
    print("=" * 80)
    print()

    change_orders = scan_change_orders()

    # Count statuses
    executed = len([co for co in change_orders if co['Status'] == 'EXECUTED'])
    folder_only = len([co for co in change_orders if 'FOLDER EXISTS' in co['Status']])
    missing = len([co for co in change_orders if co['Status'] == 'MISSING'])

    print()
    print("SUMMARY:")
    print("-" * 80)
    print(f"Total COs (001-189):     189")
    print(f"Executed PDFs Found:     {executed}")
    print(f"Folder Only (No PDF):    {folder_only}")
    print(f"Missing Completely:      {missing}")
    print()

    # Show missing COs
    if missing > 0 or folder_only > 0:
        print("ISSUES FOUND:")
        print("-" * 80)

        if missing > 0:
            missing_list = [co['CO_Number'] for co in change_orders if co['Status'] == 'MISSING']
            print(f"Missing COs: {', '.join(missing_list)}")
            print()

        if folder_only > 0:
            folder_only_list = [co['CO_Number'] for co in change_orders if 'FOLDER EXISTS' in co['Status']]
            print(f"Folder exists but no executed PDF: {', '.join(folder_only_list)}")
            print()

    # Save to CSV
    import csv
    output_file = '/Users/z/Desktop/git/montlake-closeout/all_change_orders_inventory.csv'

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['CO_Number', 'Status', 'Filename', 'Folder', 'Size_MB', 'Modified_Date', 'Full_Path', 'Notes']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(change_orders)

    print(f"💾 Saved to: {output_file}")
    print()
    print("=" * 80)

if __name__ == "__main__":
    main()
