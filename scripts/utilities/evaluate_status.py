#!/usr/bin/env python3
"""
Script to evaluate and update status for requirements in current.csv
Based on milestone progression and timing relationships
"""

import csv
from collections import Counter
from datetime import datetime

def determine_status(relation_to, milestone, timing_deadline, current_status):
    """
    Determine the appropriate status based on milestone and timing.

    Rules:
    - Preserve existing status values (don't overwrite)
    - Due: Prior to/At Substantial Completion, or By [past date]
    - In Progress: Prior to/At/Through/Until Physical Completion
    - Not Started: Everything else (later milestones)
    """

    # If status already exists, preserve it
    if current_status and current_status.strip():
        return current_status.strip()

    # Normalize inputs
    relation = (relation_to or "").strip()
    milestone_val = (milestone or "").strip()
    timing = (timing_deadline or "").strip()

    # Combine for easier matching
    combined = f"{relation} {milestone_val}".lower()

    # DUE - Items that should be completed by now (awaiting manual verification)
    if any(phrase in combined for phrase in [
        "prior to substantial completion",
        "at substantial completion",
        "before substantial completion"
    ]):
        return "Due"

    # Check for specific past dates
    if "by" in relation.lower() and "2023" in timing:
        return "Due"

    # IN PROGRESS - Items being actively worked on
    if any(phrase in combined for phrase in [
        "prior to physical completion",
        "at physical completion",
        "through physical completion",
        "until physical completion",
        "during",
        "to achieve physical completion"
    ]):
        return "In Progress"

    # NOT STARTED - Future milestones
    if any(phrase in combined for phrase in [
        "completion",  # Just "Completion" milestone (not Physical Completion)
        "final acceptance",
        "handover"
    ]):
        # But exclude if it's Physical Completion
        if "physical completion" not in combined:
            return "Not Started"

    # Check timing field for additional context
    timing_lower = timing.lower()
    if "substantial completion" in timing_lower:
        if any(word in timing_lower for word in ["prior", "before", "at"]):
            return "Due"

    if "physical completion" in timing_lower:
        return "In Progress"

    if any(milestone_name in timing_lower for milestone_name in [
        "completion date", "final acceptance", "retainage release"
    ]):
        if "physical completion" not in timing_lower:
            return "Not Started"

    # Default to Not Started for unclear cases
    return "Not Started"


def main():
    input_file = "/Users/z/Desktop/git/current.csv"
    output_file = "/Users/z/Desktop/git/current_updated.csv"

    rows = []
    status_changes = []
    status_counts = Counter()

    # Read CSV (try different encodings)
    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    f = None
    for encoding in encodings:
        try:
            f = open(input_file, 'r', encoding=encoding)
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            print(f"Successfully opened file with {encoding} encoding")
            break
        except UnicodeDecodeError:
            if f:
                f.close()
            continue

    if not f:
        raise ValueError("Could not decode file with any common encoding")

    for row in reader:
        old_status = row.get('Status', '').strip()

        # Determine new status
        new_status = determine_status(
            row.get('Relation To'),
            row.get('Milestone'),
            row.get('Timing/Deadline'),
            old_status
        )

        # Track if we made a change
        if not old_status and new_status:
            status_changes.append({
                'req_id': row.get('Req ID'),
                'description': row.get('Simple Description', '')[:60],
                'timing': row.get('Timing/Deadline'),
                'new_status': new_status
            })

        # Update the row
        row['Status'] = new_status
        status_counts[new_status] += 1
        rows.append(row)

    # Write updated CSV
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    # Generate summary report
    print("=" * 80)
    print("STATUS EVALUATION SUMMARY")
    print("=" * 80)
    print(f"\nTotal Requirements: {len(rows)}")
    print(f"Status Updates Made: {len(status_changes)}")
    print(f"\nStatus Distribution:")
    print("-" * 40)
    for status, count in sorted(status_counts.items()):
        percentage = (count / len(rows)) * 100
        print(f"  {status:15} {count:3} ({percentage:5.1f}%)")

    print(f"\n\nSample of Status Changes (showing first 20):")
    print("-" * 80)
    for i, change in enumerate(status_changes[:20], 1):
        print(f"\n{i}. {change['req_id']}: {change['new_status']}")
        print(f"   Timing: {change['timing']}")
        print(f"   Description: {change['description']}...")

    if len(status_changes) > 20:
        print(f"\n... and {len(status_changes) - 20} more changes")

    print(f"\n{'=' * 80}")
    print(f"Updated CSV saved to: {output_file}")
    print(f"{'=' * 80}\n")


if __name__ == "__main__":
    main()
