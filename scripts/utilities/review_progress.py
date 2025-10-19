#!/usr/bin/env python3
"""
Generate progress report from appendix review tracker
Shows what's been reviewed and what's remaining
"""

import pandas as pd
from datetime import datetime

def generate_progress_report():
    """Generate and display progress report"""

    tracker_file = '/Users/z/Desktop/git/montlake-closeout/appendices_review_tracker.csv'

    print("📊 Appendix Review Progress Report")
    print("=" * 80)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print()

    try:
        df = pd.read_csv(tracker_file)
    except FileNotFoundError:
        print("❌ Tracker file not found. Run create_review_tracker.py first.")
        return

    total = len(df)

    # Count by status
    status_counts = df['Review_Status'].value_counts()

    not_started = status_counts.get('Not Started', 0)
    in_progress = status_counts.get('In Progress', 0)
    reviewed = status_counts.get('Reviewed', 0)
    na = status_counts.get('N/A', 0)

    # Calculate percentages
    pct_reviewed = (reviewed / total * 100) if total > 0 else 0
    pct_in_progress = (in_progress / total * 100) if total > 0 else 0
    pct_not_started = (not_started / total * 100) if total > 0 else 0

    print("OVERALL PROGRESS:")
    print("-" * 80)
    print(f"Total Files:      {total:5}")
    print(f"Reviewed:         {reviewed:5} ({pct_reviewed:5.1f}%)")
    print(f"In Progress:      {in_progress:5} ({pct_in_progress:5.1f}%)")
    print(f"Not Started:      {not_started:5} ({pct_not_started:5.1f}%)")
    print(f"N/A:              {na:5}")
    print()

    # Progress bar
    total_to_review = total - na
    completed = reviewed
    if total_to_review > 0:
        progress = completed / total_to_review * 100
        bar_length = 50
        filled = int(bar_length * completed / total_to_review)
        bar = '█' * filled + '░' * (bar_length - filled)
        print(f"Progress: [{bar}] {progress:.1f}%")
        print()

    # By priority
    print("PROGRESS BY PRIORITY:")
    print("-" * 80)

    for priority in ['HIGH', 'MEDIUM', 'LOW']:
        priority_df = df[df['Priority'] == priority]
        if len(priority_df) > 0:
            p_total = len(priority_df)
            p_reviewed = len(priority_df[priority_df['Review_Status'] == 'Reviewed'])
            p_in_progress = len(priority_df[priority_df['Review_Status'] == 'In Progress'])
            p_not_started = len(priority_df[priority_df['Review_Status'] == 'Not Started'])
            p_na = len(priority_df[priority_df['Review_Status'] == 'N/A'])

            p_pct = (p_reviewed / p_total * 100) if p_total > 0 else 0

            print(f"{priority:8} Priority: {p_reviewed:4}/{p_total:4} ({p_pct:5.1f}%)")
            print(f"              In Progress: {p_in_progress:4} | Not Started: {p_not_started:4} | N/A: {p_na:4}")
            print()

    # By category
    print("PROGRESS BY CATEGORY:")
    print("-" * 80)

    category_stats = []
    for category in sorted(df['Category'].unique()):
        cat_df = df[df['Category'] == category]
        c_total = len(cat_df)
        c_reviewed = len(cat_df[cat_df['Review_Status'] == 'Reviewed'])
        c_in_progress = len(cat_df[cat_df['Review_Status'] == 'In Progress'])
        c_pct = (c_reviewed / c_total * 100) if c_total > 0 else 0

        priority = cat_df['Priority'].iloc[0]

        category_stats.append({
            'Category': category,
            'Priority': priority,
            'Total': c_total,
            'Reviewed': c_reviewed,
            'In Progress': c_in_progress,
            'Pct': c_pct
        })

    # Sort by priority then percentage
    priority_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
    category_stats = sorted(category_stats, key=lambda x: (priority_order[x['Priority']], -x['Pct']))

    for stat in category_stats:
        status_icon = "✅" if stat['Pct'] == 100 else "🔄" if stat['In Progress'] > 0 else "⏸️"
        print(f"{status_icon} {stat['Category']:45} {stat['Reviewed']:4}/{stat['Total']:4} ({stat['Pct']:5.1f}%)")

    print()

    # Closeout requirements found
    requirements_found = df[df['Closeout_Requirements_Found'].notna() & (df['Closeout_Requirements_Found'] != '')]

    if len(requirements_found) > 0:
        print("CLOSEOUT REQUIREMENTS IDENTIFIED:")
        print("-" * 80)
        print(f"Files with requirements documented: {len(requirements_found)}")
        print()

        for _, row in requirements_found.iterrows():
            print(f"• {row['Category']} - {row['Appendix_Number']} - {row['Filename']}")
            print(f"  Requirements: {row['Closeout_Requirements_Found']}")
            if row['Notes']:
                print(f"  Notes: {row['Notes']}")
            print()

    # Follow-up required
    follow_up = df[df['Follow_Up_Required'].fillna('').astype(str).str.upper() == 'YES']

    if len(follow_up) > 0:
        print("FOLLOW-UP REQUIRED:")
        print("-" * 80)
        for _, row in follow_up.iterrows():
            print(f"• {row['Category']} - {row['Appendix_Number']} - {row['Filename']}")
            if row['Notes']:
                print(f"  Notes: {row['Notes']}")
            print()

    # Recently reviewed
    recent = df[(df['Review_Status'] == 'Reviewed') & (df['Review_Date'] != '')]
    if len(recent) > 0:
        print("RECENTLY REVIEWED:")
        print("-" * 80)
        recent_sorted = recent.sort_values('Review_Date', ascending=False).head(10)
        for _, row in recent_sorted.iterrows():
            reviewer_info = f" by {row['Reviewer']}" if row['Reviewer'] else ""
            print(f"• {row['Review_Date']} - {row['Category']} - {row['Filename']}{reviewer_info}")
        print()

    print("=" * 80)
    print()
    print("📋 To update tracker:")
    print("   1. Open appendices_review_tracker.csv in Excel")
    print("   2. Update Review_Status, Notes, Closeout_Requirements_Found, etc.")
    print("   3. Save the file")
    print("   4. Run this script again to see updated progress")
    print()

if __name__ == "__main__":
    generate_progress_report()
