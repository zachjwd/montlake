"""
Montlake Closeout Dashboard Generator (v3)

This script generates an interactive dashboard for tracking project closeout requirements.
Output is written to /Users/z/Desktop/montlake_closeout.html

IMPORTANT: To update GitHub Pages:
1. Run this script from /Users/z/Desktop/montlake-closeout/ directory
2. Copy output to index.html: cp /Users/z/Desktop/montlake_closeout.html index.html
3. Commit and push: git add -A && git commit -m "Update dashboard" && git push

The script must be run from the montlake-closeout directory to ensure the copy
command works correctly for GitHub Pages deployment.
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from datetime import datetime
import numpy as np

# Read data (headers now in row 1)
# Updated to read from current_updated.csv in the repository
df = pd.read_csv('current_updated.csv', encoding='latin-1')

# Filter out non-applicable rows
# Remove rows where Req ID is blank
df = df[df['Req ID'].notna()]
# Remove VACANT sections
df = df[df['Subsection Title'] != 'VACANT']
# Remove NO COMPLETION REQUIREMENTS IDENTIFIED sections
df = df[df['Subsection Title'] != 'NO COMPLETION REQUIREMENTS IDENTIFIED']

# Clean up Status values
df['Status'] = df['Status'].replace({'Ongoign': 'Ongoing'})
df['Status'] = df['Status'].fillna('Not Started')

# Define completion status
completed_statuses = ['Complete']
in_progress_statuses = ['Ongoing', 'Due', 'In Progress', 'Past Due', 'Located']
df['Is_Complete'] = df['Status'].isin(completed_statuses)
df['Is_InProgress'] = df['Status'].isin(in_progress_statuses)
df['Is_NotStarted'] = ~(df['Is_Complete'] | df['Is_InProgress'])

# Calculate overall metrics
total_items = len(df)
completed_items = df['Is_Complete'].sum()
in_progress_items = df['Is_InProgress'].sum()
not_started_items = df['Is_NotStarted'].sum()
overall_completion = (completed_items / total_items * 100) if total_items > 0 else 0

# Calculate completion by Phase
category_stats = df.groupby('Category').agg({
    'Is_Complete': 'sum',
    'Is_InProgress': 'sum',
    'Is_NotStarted': 'sum',
    'Req ID': 'count'
}).reset_index()
category_stats.columns = ['Phase', 'Completed', 'In Progress', 'Not Started', 'Total']
category_stats['Completion_Pct'] = (category_stats['Completed'] / category_stats['Total'] * 100).round(1)
category_stats = category_stats[category_stats['Phase'].notna()]
category_stats = category_stats.sort_values('Total', ascending=False)

# Calculate completion by Milestone
milestone_stats = df.groupby('Milestone').agg({
    'Is_Complete': 'sum',
    'Is_InProgress': 'sum',
    'Is_NotStarted': 'sum',
    'Req ID': 'count'
}).reset_index()
milestone_stats.columns = ['Milestone', 'Completed', 'In Progress', 'Not Started', 'Total']
milestone_stats['Completion_Pct'] = (milestone_stats['Completed'] / milestone_stats['Total'] * 100).round(1)
milestone_stats = milestone_stats[milestone_stats['Milestone'].notna()]

# Define chronological order for milestones (top to bottom)
milestone_order = [
    'Substantial Completion',
    'Physical Completion',
    'Handover',
    'Completion',
    'Final Acceptance'
]

# Create order mapping for chronological display (top to bottom in chart)
milestone_stats['Order'] = milestone_stats['Milestone'].apply(
    lambda x: milestone_order.index(x) if x in milestone_order else 999
)
milestone_stats = milestone_stats.sort_values('Order', ascending=True)
milestone_stats = milestone_stats.drop('Order', axis=1)
# Reverse for horizontal bar chart display (first item appears at bottom)
milestone_stats = milestone_stats.iloc[::-1]

# Calculate completion by Section (top issues)
section_stats = df.groupby('Section').agg({
    'Is_Complete': 'sum',
    'Is_InProgress': 'sum',
    'Is_NotStarted': 'sum',
    'Req ID': 'count'
}).reset_index()
section_stats.columns = ['Section', 'Completed', 'In Progress', 'Not Started', 'Total']
section_stats['Completion_Pct'] = (section_stats['Completed'] / section_stats['Total'] * 100).round(1)
section_stats = section_stats[section_stats['Section'].notna()]
section_stats = section_stats.sort_values('Completion_Pct', ascending=True)

# Show all sections and sort by section number
top_sections = section_stats.copy()
# Create a numeric sort key by extracting and converting the section number
def section_sort_key(section):
    import re
    match = re.match(r'^(\d+)[-\.](\d+)', str(section))
    if match:
        return (int(match.group(1)), int(match.group(2)))
    return (999, 999)
top_sections['sort_key'] = top_sections['Section'].apply(section_sort_key)
top_sections = top_sections.sort_values('sort_key', ascending=False).drop('sort_key', axis=1)

# Split sections into two columns (flip so left has lower numbers)
mid_point = len(top_sections) // 2
sections_col1 = top_sections.iloc[mid_point:]  # Right half (lower numbers) goes to col1
sections_col2 = top_sections.iloc[:mid_point]  # Left half (higher numbers) goes to col2

# Calculate completion by Format
deliverable_stats = df.groupby('Deliverable Type').agg({
    'Is_Complete': 'sum',
    'Is_InProgress': 'sum',
    'Is_NotStarted': 'sum',
    'Req ID': 'count'
}).reset_index()
deliverable_stats.columns = ['Format', 'Completed', 'In Progress', 'Not Started', 'Total']
deliverable_stats['Completion_Pct'] = (deliverable_stats['Completed'] / deliverable_stats['Total'] * 100).round(1)
deliverable_stats = deliverable_stats[deliverable_stats['Format'].notna()]
deliverable_stats = deliverable_stats.sort_values('Total', ascending=False).head(15)

# Calculate max x-axis value for consistent scaling across all three charts
max_x_value = max(
    category_stats['Total'].max(),
    top_sections['Total'].max(),
    deliverable_stats['Total'].max()
)

# Responsible Party analysis - group similar parties
def group_responsible_party(party):
    if pd.isna(party):
        return 'Unknown'
    party_str = str(party)
    if 'Design-Builder' in party_str or 'Design Builder' in party_str:
        return 'Design-Builder'
    elif 'WSDOT' in party_str:
        return 'WSDOT'
    else:
        return party_str

df['Grouped_Party'] = df['Responsibility'].apply(group_responsible_party)

party_stats = df.groupby('Grouped_Party').agg({
    'Is_Complete': 'sum',
    'Is_InProgress': 'sum',
    'Is_NotStarted': 'sum',
    'Req ID': 'count'
}).reset_index()
party_stats.columns = ['Responsible Party', 'Completed', 'In Progress', 'Not Started', 'Total']
party_stats['Completion_Pct'] = (party_stats['Completed'] / party_stats['Total'] * 100).round(1)
party_stats = party_stats[party_stats['Responsible Party'].notna()]
party_stats = party_stats.sort_values('Total', ascending=False)

# Create dashboard with tabs-like structure
from plotly.subplots import make_subplots

# Create main figure
fig = go.Figure()

# Color scheme - Professional status colors
COLOR_COMPLETE = '#10b981'  # Green (matches KPI card)
COLOR_IN_PROGRESS = '#facc15'  # Yellow (high contrast)
COLOR_NOT_STARTED = '#f87171'  # Red (clear warning color)
COLOR_PRIMARY = '#1e40af'  # Blue

# ==================== EXECUTIVE SUMMARY PAGE ====================

# KPI Cards (using annotations for a cleaner look)
fig.add_trace(go.Scatter(
    x=[0], y=[0],
    mode='markers',
    marker=dict(size=0.1, color='white'),
    showlegend=False,
    hoverinfo='skip'
))

# Add title
title_text = f"""<b style='font-size:32px'>MONTLAKE PROJECT CLOSEOUT DASHBOARD</b><br>
<span style='font-size:14px; color:gray'>Executive Summary - Generated {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</span>"""

# Create a multi-page HTML with tabs
html_header = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Montlake Closeout Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <link rel="stylesheet" href="https://cdn.datatables.net/1.13.7/css/jquery.dataTables.min.css">
    <link rel="stylesheet" href="https://cdn.datatables.net/colreorder/1.7.0/css/colReorder.dataTables.min.css">
    <link rel="stylesheet" href="https://cdn.datatables.net/buttons/2.4.2/css/buttons.dataTables.min.css">
    <script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
    <script src="https://cdn.datatables.net/1.13.7/js/jquery.dataTables.min.js"></script>
    <script src="https://cdn.datatables.net/colreorder/1.7.0/js/dataTables.colReorder.min.js"></script>
    <script src="https://cdn.datatables.net/buttons/2.4.2/js/dataTables.buttons.min.js"></script>
    <script src="https://cdn.datatables.net/buttons/2.4.2/js/buttons.colVis.min.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            margin: 0;
            padding: 0;
            background: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
            color: white;
            padding: 30px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header h1 {{
            margin: 0;
            font-size: 32px;
            font-weight: 700;
        }}
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
            font-size: 14px;
        }}
        .project-timeline {{
            background: rgba(255,255,255,0.1);
            padding: 30px;
            margin: 20px auto 0 auto;
            max-width: 1200px;
            border-radius: 8px;
        }}
        .timeline-container {{
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            position: relative;
            margin-top: 20px;
        }}
        .timeline-line {{
            position: absolute;
            top: 25px;
            left: 60px;
            right: 60px;
            height: 3px;
            background: rgba(255,255,255,0.3);
            z-index: 0;
        }}
        .timeline-milestone {{
            position: relative;
            z-index: 1;
            text-align: center;
            flex: 1;
        }}
        .timeline-icon {{
            width: 50px;
            height: 50px;
            border-radius: 50%;
            margin: 0 auto 10px auto;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            background: rgba(255,255,255,0.2);
            border: 3px solid rgba(255,255,255,0.4);
            position: relative;
            z-index: 2;
        }}
        .timeline-icon span {{
            line-height: 1;
        }}
        .timeline-icon.achieved {{
            background: #059669;
            border-color: #059669;
        }}
        .timeline-icon.target {{
            background: rgba(255,255,255,0.15);
            border-color: rgba(255,255,255,0.5);
        }}
        .timeline-label {{
            font-size: 11px;
            opacity: 0.9;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 5px;
        }}
        .timeline-date {{
            font-size: 14px;
            font-weight: 600;
            min-width: 100px;
        }}
        .timeline-status {{
            font-size: 12px;
            opacity: 0.85;
            margin-top: 3px;
        }}
        .kpi-container {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 30px;
            max-width: 1400px;
            margin: 0 auto;
        }}
        .kpi-card {{
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .kpi-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 4px 16px rgba(0,0,0,0.15);
        }}
        .kpi-label {{
            font-size: 14px;
            color: #6b7280;
            font-weight: 500;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .kpi-value {{
            font-size: 36px;
            font-weight: 700;
            color: #111827;
            margin-bottom: 8px;
        }}
        .kpi-subtitle {{
            font-size: 14px;
            color: #9ca3af;
        }}
        .complete {{ color: #10b981; }}
        .in-progress {{ color: #f59e0b; }}
        .not-started {{ color: #ef4444; }}

        .tabs {{
            background: white;
            padding: 0;
            margin: 0 30px;
            border-radius: 12px 12px 0 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            display: flex;
            overflow: hidden;
        }}
        .tab {{
            flex: 1;
            padding: 18px 24px;
            cursor: pointer;
            border: none;
            background: #f9fafb;
            color: #6b7280;
            font-size: 15px;
            font-weight: 600;
            transition: all 0.3s;
            border-bottom: 3px solid transparent;
        }}
        .tab:hover {{
            background: #f3f4f6;
            color: #3b82f6;
        }}
        .tab.active {{
            background: white;
            color: #3b82f6;
            border-bottom: 3px solid #3b82f6;
        }}
        .tab-content {{
            display: none;
            background: white;
            margin: 0 30px 30px 30px;
            padding: 30px;
            border-radius: 0 0 12px 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .tab-content.active {{
            display: block;
        }}
        .tab-content.full-width {{
            margin: 0;
            padding: 20px 0;
            border-radius: 0;
            box-shadow: none;
            max-width: 100%;
        }}
        #details_table {{
            width: 100% !important;
        }}
        #details_table .plotly {{
            width: 100% !important;
        }}
        .chart-container {{
            margin-bottom: 30px;
        }}
        .chart-title {{
            font-size: 20px;
            font-weight: 700;
            color: #111827;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e5e7eb;
        }}
        .progress-bar {{
            width: 100%;
            height: 8px;
            background: #e5e7eb;
            border-radius: 4px;
            overflow: hidden;
            margin-top: 8px;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #10b981 0%, #059669 100%);
            transition: width 0.3s;
        }}
        .alert {{
            background: #fef2f2;
            border-left: 4px solid #ef4444;
            padding: 16px;
            margin: 20px 0;
            border-radius: 8px;
        }}
        .alert-title {{
            font-weight: 700;
            color: #991b1b;
            margin-bottom: 8px;
        }}
        .alert-text {{
            color: #7f1d1d;
            font-size: 14px;
        }}

        /* DataTables styling */
        #requirements_table {{
            font-size: 13px;
        }}
        #requirements_table thead th {{
            background: #1e40af;
            color: white;
            padding: 12px 8px;
            font-weight: 600;
            position: relative;
        }}
        #requirements_table thead tr:nth-child(2) th {{
            background: white;
            padding: 4px;
            position: relative;
        }}
        .filter-button {{
            width: 100%;
            padding: 6px 24px 6px 8px;
            font-size: 12px;
            border: 1px solid #d1d5db;
            border-radius: 4px;
            background: white;
            cursor: pointer;
            text-align: left;
            position: relative;
        }}
        .filter-button:hover {{
            background: #f9fafb;
        }}
        .filter-button::after {{
            content: '▼';
            position: absolute;
            right: 8px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 10px;
            color: #6b7280;
        }}
        .filter-dropdown {{
            position: absolute;
            top: 100%;
            left: 0;
            background: white;
            border: 2px solid #1e40af;
            border-radius: 4px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 1000;
            display: none;
            min-width: 200px;
            max-width: 300px;
        }}
        .filter-dropdown.active {{
            display: block;
        }}
        .filter-search {{
            padding: 8px;
            border-bottom: 1px solid #e5e7eb;
        }}
        .filter-search input {{
            width: 100%;
            padding: 6px 8px;
            border: 1px solid #d1d5db;
            border-radius: 4px;
            font-size: 12px;
        }}
        .filter-options {{
            max-height: 250px;
            overflow-y: auto;
            padding: 4px;
        }}
        .filter-option {{
            padding: 6px 8px;
            display: flex;
            align-items: center;
            cursor: pointer;
            font-size: 13px;
            color: #111827;
        }}
        .filter-option:hover {{
            background: #f3f4f6;
        }}
        .filter-option input[type="checkbox"] {{
            margin-right: 8px;
            cursor: pointer;
        }}
        .filter-option span {{
            color: #111827;
        }}
        .filter-actions {{
            padding: 8px;
            border-top: 1px solid #e5e7eb;
            display: flex;
            gap: 8px;
        }}
        .filter-actions button {{
            flex: 1;
            padding: 6px 12px;
            font-size: 12px;
            border: 1px solid #d1d5db;
            border-radius: 4px;
            background: white;
            cursor: pointer;
        }}
        .filter-actions button:hover {{
            background: #f3f4f6;
        }}
        .filter-actions button.primary {{
            background: #1e40af;
            color: white;
            border-color: #1e40af;
        }}
        .filter-actions button.primary:hover {{
            background: #1e3a8a;
        }}
        #requirements_table tbody td {{
            padding: 10px 8px;
        }}
        #requirements_table tbody tr:nth-child(even) {{
            background-color: #f9fafb;
        }}
        #requirements_table tbody tr:hover {{
            background-color: #e5e7eb;
        }}

        /* Make Simple Description column wider */
        #requirements_table .simple-description-col {{
            min-width: 300px;
            max-width: 450px;
            white-space: normal;
        }}

        /* Requirement detail row styling */
        .requirement-detail-row {{
            background-color: #f9fafb !important;
        }}

        .requirement-detail-cell {{
            padding: 10px 40px !important;
            font-size: 13px !important;
            line-height: 1.6 !important;
            border-top: none !important;
        }}

        .section-reference {{
            font-weight: 600;
            color: #3b82f6;
            margin-right: 8px;
        }}

        .requirement-description {{
            color: #374151;
        }}

        .dataTables_wrapper {{
            padding: 0;
        }}
        .dataTables_filter {{
            margin-bottom: 20px;
        }}
        .dataTables_filter input {{
            border: 2px solid #e5e7eb;
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 14px;
            width: 300px;
        }}
        .dataTables_length select {{
            border: 2px solid #e5e7eb;
            border-radius: 6px;
            padding: 6px 10px;
            font-size: 14px;
        }}
        .dataTables_info {{
            color: #6b7280;
            font-size: 14px;
        }}
        .dataTables_paginate {{
            margin-top: 20px;
        }}
        .dataTables_paginate .paginate_button {{
            padding: 6px 12px;
            margin: 0 2px;
            border-radius: 6px;
            border: 1px solid #e5e7eb;
            background: white;
            color: #1e40af;
        }}
        .dataTables_paginate .paginate_button.current {{
            background: #1e40af;
            color: white;
            border-color: #1e40af;
        }}
        .dataTables_paginate .paginate_button:hover {{
            background: #f3f4f6;
        }}

        /* Column selector styling */
        .column-selector {{
            background: #f9fafb;
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }}
        .column-selector h3 {{
            margin: 0 0 15px 0;
            color: #1e40af;
            font-size: 16px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .column-selector h3:hover {{
            color: #1e3a8a;
        }}
        .column-selector-content {{
            display: block;
        }}
        .column-selector-content.collapsed {{
            display: none;
        }}
        .collapse-icon {{
            transition: transform 0.3s;
        }}
        .collapse-icon.collapsed {{
            transform: rotate(-90deg);
        }}
        .column-list {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 10px;
            margin-bottom: 15px;
        }}
        .column-item {{
            display: flex;
            align-items: center;
            padding: 8px;
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 6px;
            cursor: move;
        }}
        .column-item input[type="checkbox"] {{
            margin-right: 8px;
            cursor: pointer;
        }}
        .column-item label {{
            cursor: pointer;
            user-select: none;
        }}
        .column-item .drag-handle {{
            color: #9ca3af;
            margin-left: 8px;
            cursor: move;
        }}
        .column-controls {{
            display: flex;
            gap: 10px;
        }}
        .btn {{
            padding: 8px 16px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.2s;
        }}
        .btn-primary {{
            background: #1e40af;
            color: white;
        }}
        .btn-primary:hover {{
            background: #1e3a8a;
        }}
        .btn-secondary {{
            background: #6b7280;
            color: white;
        }}
        .btn-secondary:hover {{
            background: #4b5563;
        }}

        /* Chart Selector Segmented Control */
        .chart-selector-btn {{
            padding: 12px 24px;
            border: 2px solid #e5e7eb;
            background: white;
            color: #6b7280;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            border-radius: 8px;
        }}
        .chart-selector-btn:hover {{
            background: #f9fafb;
            border-color: #3b82f6;
            color: #3b82f6;
        }}
        .chart-selector-btn.active {{
            background: #3b82f6;
            border-color: #3b82f6;
            color: white;
        }}
        .chart-view {{
            min-height: 400px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>MONTLAKE PROJECT CLOSEOUT DASHBOARD</h1>
        <p>Executive Summary - Generated {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        <div class="project-timeline">
            <div class="timeline-container">
                <div class="timeline-line"></div>

                <div class="timeline-milestone">
                    <div class="timeline-icon achieved"><span>🏗️</span></div>
                    <div class="timeline-label">Project Start</div>
                    <div class="timeline-date">Nov 15, 2018</div>
                </div>

                <div class="timeline-milestone">
                    <div class="timeline-icon achieved"><span>✓</span></div>
                    <div class="timeline-label">Substantial Completion</div>
                    <div class="timeline-date">May 1, 2025</div>
                    <div class="timeline-status">Achieved</div>
                </div>

                <div class="timeline-milestone">
                    <div class="timeline-icon target"><span>📅</span></div>
                    <div class="timeline-label">Physical Completion</div>
                    <div class="timeline-date">Dec 31, 2025</div>
                    <div class="timeline-status">Contract Date</div>
                </div>

                <div class="timeline-milestone">
                    <div class="timeline-icon target"><span>📅</span></div>
                    <div class="timeline-label">Completion</div>
                    <div class="timeline-date">TBD</div>
                    <div class="timeline-status">Pending</div>
                </div>

                <div class="timeline-milestone">
                    <div class="timeline-icon target"><span>🏁</span></div>
                    <div class="timeline-label">Final Acceptance</div>
                    <div class="timeline-date">TBD</div>
                    <div class="timeline-status">Pending</div>
                </div>
            </div>
        </div>
    </div>

    <div class="kpi-container">
        <div class="kpi-card">
            <div class="kpi-label">Completed</div>
            <div class="kpi-value complete">{completed_items} of {total_items}</div>
            <div class="kpi-subtitle">{(completed_items/total_items*100):.1f}% of total requirements</div>
        </div>

        <div class="kpi-card">
            <div class="kpi-label">In Progress</div>
            <div class="kpi-value in-progress">{in_progress_items}</div>
            <div class="kpi-subtitle">{(in_progress_items/total_items*100):.1f}% of total requirements</div>
        </div>

        <div class="kpi-card">
            <div class="kpi-label">Not Started</div>
            <div class="kpi-value not-started">{not_started_items}</div>
            <div class="kpi-subtitle">{(not_started_items/total_items*100):.1f}% of total requirements</div>
        </div>
    </div>

"""

# Generate individual charts
charts_html = ""

# ===== OVERVIEW TAB =====
# Overall status breakdown (horizontal bar)
overview_fig = go.Figure()

overview_fig.add_trace(go.Bar(
    name='Completed',
    y=['Overall Status'],
    x=[completed_items],
    orientation='h',
    marker_color=COLOR_COMPLETE,
    text=[completed_items],
    textposition='inside',
    hovertemplate=f'<b>Completed</b><br>{completed_items} items ({(completed_items/total_items*100):.1f}%)<extra></extra>',
    showlegend=True
))

overview_fig.add_trace(go.Bar(
    name='In Progress',
    y=['Overall Status'],
    x=[in_progress_items],
    orientation='h',
    marker_color=COLOR_IN_PROGRESS,
    text=[in_progress_items],
    textposition='inside',
    hovertemplate=f'<b>In Progress</b><br>{in_progress_items} items ({(in_progress_items/total_items*100):.1f}%)<extra></extra>',
    showlegend=True
))

overview_fig.add_trace(go.Bar(
    name='Not Started',
    y=['Overall Status'],
    x=[not_started_items],
    orientation='h',
    marker_color=COLOR_NOT_STARTED,
    text=[not_started_items],
    textposition='inside',
    hovertemplate=f'<b>Not Started</b><br>{not_started_items} items ({(not_started_items/total_items*100):.1f}%)<extra></extra>',
    showlegend=True
))

overview_fig.update_layout(
    barmode='stack',
    title=dict(text='Overall Status', font=dict(size=16), x=0.5, xanchor='center'),
    xaxis=dict(title='Number of Requirements'),
    yaxis=dict(showticklabels=False),
    height=400,
    showlegend=False,
    plot_bgcolor='white',
    paper_bgcolor='white'
)

# Overview tab will be combined with milestone and party charts - placeholder for now

# ===== CATEGORY TAB =====
category_fig = go.Figure()

category_fig.add_trace(go.Bar(
    name='Completed',
    y=category_stats['Phase'].tolist(),
    x=category_stats['Completed'].tolist(),
    orientation='h',
    marker_color=COLOR_COMPLETE,
    text=category_stats['Completed'].tolist(),
    textposition='inside',
    hovertemplate='<b>%{y}</b><br>Completed: %{x}<extra></extra>'
))

category_fig.add_trace(go.Bar(
    name='In Progress',
    y=category_stats['Phase'].tolist(),
    x=category_stats['In Progress'].tolist(),
    orientation='h',
    marker_color=COLOR_IN_PROGRESS,
    text=category_stats['In Progress'].tolist(),
    textposition='inside',
    hovertemplate='<b>%{y}</b><br>In Progress: %{x}<extra></extra>'
))

category_fig.add_trace(go.Bar(
    name='Not Started',
    y=category_stats['Phase'].tolist(),
    x=category_stats['Not Started'].tolist(),
    orientation='h',
    marker_color=COLOR_NOT_STARTED,
    text=category_stats['Not Started'].tolist(),
    textposition='inside',
    hovertemplate='<b>%{y}</b><br>Not Started: %{x}<extra></extra>'
))

category_fig.update_layout(
    barmode='stack',
    title=dict(text='', font=dict(size=16), x=0.5, xanchor='center'),
    xaxis=dict(title='Number of Requirements'),
    yaxis=dict(title='', automargin=False),
    height=500,
    autosize=True,
    showlegend=False,
    bargap=0.1,
    plot_bgcolor='white',
    paper_bgcolor='white',
    margin=dict(l=250, r=20, t=10, b=80)
)

# Category completion percentage
category_pct_fig = go.Figure()

category_pct_fig.add_trace(go.Bar(
    y=category_stats['Phase'].tolist(),
    x=category_stats['Completion_Pct'],
    orientation='h',
    marker=dict(
        color=category_stats['Completion_Pct'],
        colorscale=[[0, COLOR_NOT_STARTED], [0.5, COLOR_IN_PROGRESS], [1, COLOR_COMPLETE]],
        showscale=False,
        line=dict(color='white', width=2)
    ),
    text=category_stats.apply(lambda row: f"{row['Completion_Pct']:.1f}% ({row['Completed']}/{row['Total']})", axis=1),
    textposition='outside',
    hovertemplate='<b>%{y}</b><br>Completion: %{x:.1f}%<extra></extra>'
))

category_pct_fig.update_layout(
    title=dict(text='Completion Percentage by Phase', font=dict(size=20)),
    xaxis=dict(title='Completion %', range=[0, max(110, category_stats['Completion_Pct'].max() + 10)]),
    yaxis=dict(title=''),
    height=500,
    plot_bgcolor='white',
    paper_bgcolor='white'
)

# Category charts will be combined with deliverable tab - removed standalone category tab

# ===== MILESTONE TAB =====
# Debug: print milestone stats
print("\n=== MILESTONE STATS DEBUG ===")
print(milestone_stats[['Milestone', 'Completed', 'In Progress', 'Not Started', 'Total']].to_string())
print("=" * 50)

milestone_fig = go.Figure()

milestone_fig.add_trace(go.Bar(
    name='Completed',
    y=milestone_stats['Milestone'].tolist(),
    x=milestone_stats['Completed'].tolist(),
    orientation='h',
    marker_color=COLOR_COMPLETE,
    text=milestone_stats['Completed'].tolist(),
    textposition='inside',
    hovertemplate='<b>%{y}</b><br>Completed: %{x}<extra></extra>'
))

milestone_fig.add_trace(go.Bar(
    name='In Progress',
    y=milestone_stats['Milestone'].tolist(),
    x=milestone_stats['In Progress'].tolist(),
    orientation='h',
    marker_color=COLOR_IN_PROGRESS,
    text=milestone_stats['In Progress'].tolist(),
    textposition='inside',
    hovertemplate='<b>%{y}</b><br>In Progress: %{x}<extra></extra>'
))

milestone_fig.add_trace(go.Bar(
    name='Not Started',
    y=milestone_stats['Milestone'].tolist(),
    x=milestone_stats['Not Started'].tolist(),
    orientation='h',
    marker_color=COLOR_NOT_STARTED,
    text=milestone_stats['Not Started'].tolist(),
    textposition='inside',
    hovertemplate='<b>%{y}</b><br>Not Started: %{x}<extra></extra>'
))

milestone_fig.update_layout(
    barmode='stack',
    title=dict(text='', font=dict(size=16), x=0.5, xanchor='center'),
    xaxis=dict(title='Number of Requirements'),
    yaxis=dict(title='', automargin=False),
    height=500,
    autosize=True,
    showlegend=False,
    plot_bgcolor='white',
    paper_bgcolor='white',
    margin=dict(l=250, r=20, t=10, b=80)
)

# Milestone tab will be combined with overview - removed standalone tab

# ===== SECTION TAB - SPLIT INTO TWO COLUMNS =====
section_fig_col1 = go.Figure()

section_fig_col1.add_trace(go.Bar(
    name='Completed',
    y=sections_col1['Section'].tolist(),
    x=sections_col1['Completed'].tolist(),
    orientation='h',
    marker_color=COLOR_COMPLETE,
    text=sections_col1['Completed'].tolist(),
    textposition='inside',
    hovertemplate='<b>%{y}</b><br>Completed: %{x}<extra></extra>'
))

section_fig_col1.add_trace(go.Bar(
    name='In Progress',
    y=sections_col1['Section'].tolist(),
    x=sections_col1['In Progress'].tolist(),
    orientation='h',
    marker_color=COLOR_IN_PROGRESS,
    text=sections_col1['In Progress'].tolist(),
    textposition='inside',
    hovertemplate='<b>%{y}</b><br>In Progress: %{x}<extra></extra>'
))

section_fig_col1.add_trace(go.Bar(
    name='Not Started',
    y=sections_col1['Section'].tolist(),
    x=sections_col1['Not Started'].tolist(),
    orientation='h',
    marker_color=COLOR_NOT_STARTED,
    text=sections_col1['Not Started'].tolist(),
    textposition='inside',
    hovertemplate='<b>%{y}</b><br>Not Started: %{x}<extra></extra>'
))

section_fig_col1.update_layout(
    barmode='stack',
    title=dict(text='', font=dict(size=16), x=0.5, xanchor='center'),
    xaxis=dict(title='Number of Requirements'),
    yaxis=dict(title='', automargin=False),
    height=500,
    autosize=True,
    showlegend=False,
    bargap=0.1,
    plot_bgcolor='white',
    paper_bgcolor='white',
    margin=dict(l=350, r=20, t=10, b=80)
)

section_fig_col2 = go.Figure()

section_fig_col2.add_trace(go.Bar(
    name='Completed',
    y=sections_col2['Section'].tolist(),
    x=sections_col2['Completed'].tolist(),
    orientation='h',
    marker_color=COLOR_COMPLETE,
    text=sections_col2['Completed'].tolist(),
    textposition='inside',
    hovertemplate='<b>%{y}</b><br>Completed: %{x}<extra></extra>'
))

section_fig_col2.add_trace(go.Bar(
    name='In Progress',
    y=sections_col2['Section'].tolist(),
    x=sections_col2['In Progress'].tolist(),
    orientation='h',
    marker_color=COLOR_IN_PROGRESS,
    text=sections_col2['In Progress'].tolist(),
    textposition='inside',
    hovertemplate='<b>%{y}</b><br>In Progress: %{x}<extra></extra>'
))

section_fig_col2.add_trace(go.Bar(
    name='Not Started',
    y=sections_col2['Section'].tolist(),
    x=sections_col2['Not Started'].tolist(),
    orientation='h',
    marker_color=COLOR_NOT_STARTED,
    text=sections_col2['Not Started'].tolist(),
    textposition='inside',
    hovertemplate='<b>%{y}</b><br>Not Started: %{x}<extra></extra>'
))

section_fig_col2.update_layout(
    barmode='stack',
    title=dict(text='', font=dict(size=16), x=0.5, xanchor='center'),
    xaxis=dict(title='Number of Requirements'),
    yaxis=dict(title='', automargin=False),
    height=500,
    autosize=True,
    showlegend=False,
    bargap=0.1,
    plot_bgcolor='white',
    paper_bgcolor='white',
    margin=dict(l=350, r=20, t=10, b=80)
)

# Section chart will be combined with deliverable tab - removed standalone section tab

# ===== DELIVERABLE TAB =====
deliverable_fig = go.Figure()

deliverable_fig.add_trace(go.Bar(
    name='Completed',
    y=deliverable_stats['Format'].tolist(),
    x=deliverable_stats['Completed'].tolist(),
    orientation='h',
    marker_color=COLOR_COMPLETE,
    text=deliverable_stats['Completed'].tolist(),
    textposition='inside',
    hovertemplate='<b>%{y}</b><br>Completed: %{x}<extra></extra>'
))

deliverable_fig.add_trace(go.Bar(
    name='In Progress',
    y=deliverable_stats['Format'].tolist(),
    x=deliverable_stats['In Progress'].tolist(),
    orientation='h',
    marker_color=COLOR_IN_PROGRESS,
    text=deliverable_stats['In Progress'].tolist(),
    textposition='inside',
    hovertemplate='<b>%{y}</b><br>In Progress: %{x}<extra></extra>'
))

deliverable_fig.add_trace(go.Bar(
    name='Not Started',
    y=deliverable_stats['Format'].tolist(),
    x=deliverable_stats['Not Started'].tolist(),
    orientation='h',
    marker_color=COLOR_NOT_STARTED,
    text=deliverable_stats['Not Started'].tolist(),
    textposition='inside',
    hovertemplate='<b>%{y}</b><br>Not Started: %{x}<extra></extra>'
))

deliverable_fig.update_layout(
    barmode='stack',
    title=dict(text='', font=dict(size=16), x=0.5, xanchor='center'),
    xaxis=dict(title='Number of Requirements'),
    yaxis=dict(title='', automargin=False),
    height=500,
    autosize=True,
    showlegend=False,
    bargap=0.1,
    plot_bgcolor='white',
    paper_bgcolor='white',
    margin=dict(l=250, r=20, t=10, b=80)
)

# Config to hide Plotly modebar
plotly_config = {'displayModeBar': False}

# ===== RESPONSIBLE PARTY CHART =====
party_fig = go.Figure()

party_fig.add_trace(go.Bar(
    name='Completed',
    y=party_stats['Responsible Party'].tolist(),
    x=party_stats['Completed'].tolist(),
    orientation='h',
    marker_color=COLOR_COMPLETE,
    text=party_stats['Completed'].tolist(),
    textposition='inside',
    hovertemplate='<b>%{y}</b><br>Completed: %{x}<extra></extra>'
))

party_fig.add_trace(go.Bar(
    name='In Progress',
    y=party_stats['Responsible Party'].tolist(),
    x=party_stats['In Progress'].tolist(),
    orientation='h',
    marker_color=COLOR_IN_PROGRESS,
    text=party_stats['In Progress'].tolist(),
    textposition='inside',
    hovertemplate='<b>%{y}</b><br>In Progress: %{x}<extra></extra>'
))

party_fig.add_trace(go.Bar(
    name='Not Started',
    y=party_stats['Responsible Party'].tolist(),
    x=party_stats['Not Started'].tolist(),
    orientation='h',
    marker_color=COLOR_NOT_STARTED,
    text=party_stats['Not Started'].tolist(),
    textposition='inside',
    hovertemplate='<b>%{y}</b><br>Not Started: %{x}<extra></extra>'
))

party_fig.update_layout(
    barmode='stack',
    title=dict(text='', font=dict(size=16), x=0.5, xanchor='center'),
    xaxis=dict(title='Number of Requirements'),
    yaxis=dict(title='', automargin=False),
    height=500,
    autosize=True,
    showlegend=False,
    plot_bgcolor='white',
    paper_bgcolor='white',
    margin=dict(l=250, r=20, t=10, b=80)
)

# ===== UNIFIED VIEW WITH TAB-STYLE CHART SELECTOR =====
charts_html += f"""
<div class="tabs">
    <button class="tab active" onclick="showChart('milestones')">📅 Milestones</button>
    <button class="tab" onclick="showChart('sections')">📑 Sections</button>
    <button class="tab" onclick="showChart('categories')">🏷️ Phase</button>
    <button class="tab" onclick="showChart('deliverables')">📦 Format</button>
    <button class="tab" onclick="showChart('party')">👥 Responsibility</button>
    <button class="tab" onclick="showChart('all')">📋 All Requirements</button>
</div>

<div style="background: white; margin: 0 30px 30px 30px; padding: 30px; border-radius: 0 0 12px 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
    <!-- Chart Containers (centered with consistent width) -->
    <div id="chart-milestones" class="chart-view active" style="display: flex; flex-direction: column; align-items: center;">
        <div style="text-align: center; margin-bottom: 10px; font-size: 16px; color: #333;">By Milestone</div>
        <div style="width: 100%; max-width: 900px; padding: 0 20px;">
            {milestone_fig.to_html(include_plotlyjs=False, div_id='milestone_chart', config=plotly_config)}
        </div>
    </div>

    <div id="chart-party" class="chart-view" style="display: none; flex-direction: column; align-items: center;">
        <div style="text-align: center; margin-bottom: 10px; font-size: 16px; color: #333;">By Responsibility</div>
        <div style="width: 100%; max-width: 900px; padding: 0 20px;">
            {party_fig.to_html(include_plotlyjs=False, div_id='party_chart', config=plotly_config)}
        </div>
    </div>

    <div id="chart-sections" class="chart-view" style="display: none; flex-direction: column; align-items: center;">
        <div style="text-align: center; margin-bottom: 10px; font-size: 16px; color: #333;">By Section</div>
        <div style="display: flex; gap: 20px; width: 100%; max-width: 1400px;">
            <div style="flex: 1;">
                {section_fig_col1.to_html(include_plotlyjs=False, div_id='section_chart_col1', config=plotly_config)}
            </div>
            <div style="flex: 1;">
                {section_fig_col2.to_html(include_plotlyjs=False, div_id='section_chart_col2', config=plotly_config)}
            </div>
        </div>
    </div>

    <div id="chart-categories" class="chart-view" style="display: none; flex-direction: column; align-items: center;">
        <div style="text-align: center; margin-bottom: 10px; font-size: 16px; color: #333;">By Phase</div>
        <div style="width: 100%; max-width: 900px; padding: 0 20px;">
            {category_fig.to_html(include_plotlyjs=False, div_id='category_chart', config=plotly_config)}
        </div>
    </div>

    <div id="chart-deliverables" class="chart-view" style="display: none; flex-direction: column; align-items: center;">
        <div style="text-align: center; margin-bottom: 10px; font-size: 16px; color: #333;">By Format</div>
        <div style="width: 100%; max-width: 900px; padding: 0 20px;">
            {deliverable_fig.to_html(include_plotlyjs=False, div_id='deliverable_chart', config=plotly_config)}
        </div>
    </div>

    <!-- All Requirements - shows table in place of chart -->
    <div id="chart-all" class="chart-view" style="display: none;">
        <div id="all-requirements-table-container" style="display: none; padding: 0 20px; width: 100%; box-sizing: border-box; overflow-x: auto;">
        </div>
    </div>

    <!-- Legend -->
    <div id="chart-legend" style="display: flex; justify-content: center; margin-top: 30px; gap: 30px; font-size: 14px;">
        <div style="display: flex; align-items: center; gap: 8px;">
            <div style="width: 20px; height: 20px; background-color: {COLOR_COMPLETE}; border-radius: 3px;"></div>
            <span>Completed</span>
        </div>
        <div style="display: flex; align-items: center; gap: 8px;">
            <div style="width: 20px; height: 20px; background-color: {COLOR_IN_PROGRESS}; border-radius: 3px;"></div>
            <span>In Progress</span>
        </div>
        <div style="display: flex; align-items: center; gap: 8px;">
            <div style="width: 20px; height: 20px; background-color: {COLOR_NOT_STARTED}; border-radius: 3px;"></div>
            <span>Not Started</span>
        </div>
    </div>

    <div id="chart-instructions" style="text-align: center; margin-top: 15px; font-size: 13px; color: #6b7280; font-style: italic;">
        Click on any colored bar segment to view detailed requirements for that specific status.
    </div>

    <!-- Unified Drill-down table -->
    <div id="drilldown" style="margin-top: 30px; display: none; padding: 0 30px;">
        <h3 id="drilldown_title" style="text-align: center; margin-bottom: 20px; margin-top: 20px;"></h3>
        <table id="drilldown_table" class="display full-width" style="width:100%">
            <thead>
                <tr>
                    <th>Status</th>
                    <th>Status Notes</th>
                    <th>Section</th>
                    <th>Subsection</th>
                    <th>Timing/Deadline</th>
                    <th>Simple Description</th>
                    <th>Specification</th>
                    <th>Phase</th>
                    <th>Responsible Party</th>
                    <th>WSDOT Lead</th>
                    <th>Notes</th>
                </tr>
            </thead>
            <tbody>
            </tbody>
        </table>
    </div>
</div>
"""

# Generate originalData array for JavaScript from the dataframe
import json
df_for_js = df.fillna('')
original_data_list = []
for _, row in df_for_js.iterrows():
    # Combine Subsection and Subsection Title
    subsection_combined = str(row['Subsection'])
    if str(row['Subsection Title']):
        subsection_combined += ' - ' + str(row['Subsection Title'])

    row_dict = {
        'Status': str(row['Status']),
        'Status Notes': str(row['Status Notes']),
        'Section': str(row['Section']),
        'Subsection': subsection_combined,
        'Timing/Deadline': str(row['Timing/Deadline']),
        'Simple Description': str(row['Simple Description']),
        'Specification': str(row['Specification']),
        'Phase': str(row['Category']),
        'Responsible Party': str(row['Responsibility']),
        'WSDOT Lead': str(row['WSDOT Lead']),
        'Notes': str(row['Notes']),
        'Milestone': str(row['Milestone']),
        'Format': str(row['Deliverable Type'])
    }
    original_data_list.append(row_dict)

original_data_json = json.dumps(original_data_list)

# Create html_footer with JavaScript
html_footer = f"""
    <script>
        var originalData = {original_data_json};

        // Show selected chart
        function showChart(chartName) {{
            // Hide all chart views
            var charts = document.getElementsByClassName('chart-view');
            for (var i = 0; i < charts.length; i++) {{
                charts[i].style.display = 'none';
            }}

            // Remove active class from all tabs
            var tabs = document.getElementsByClassName('tab');
            for (var i = 0; i < tabs.length; i++) {{
                tabs[i].classList.remove('active');
            }}

            // Show selected chart
            document.getElementById('chart-' + chartName).style.display = 'flex';

            // Add active class to clicked tab
            event.target.classList.add('active');

            // If All Requirements tab, show the table in place of the chart
            if (chartName === 'all') {{
                // Hide legend and instructions for All Requirements
                $('#chart-legend').hide();
                $('#chart-instructions').hide();

                // Move the drilldown table into the chart-all container
                $('#all-requirements-table-container').html($('#drilldown'));
                $('#all-requirements-table-container').show();
                $('#drilldown').show();
                $('#drilldown').css({{
                    'margin-top': '0px',
                    'padding': '0'
                }});
                $('#drilldown_title').css({{
                    'margin-top': '0px',
                    'margin-bottom': '0px'
                }});
                $('#drilldown_title').text('');

                // Populate table with all data
                if ($.fn.DataTable.isDataTable('#drilldown_table')) {{
                    $('#drilldown_table').DataTable().destroy();
                }}

                var tbody = $('#drilldown_table tbody');
                tbody.empty();
                originalData.forEach(function(row) {{
                    var tr = '<tr>';
                    tr += '<td>' + (row['Status'] || '') + '</td>';
                    tr += '<td>' + (row['Status Notes'] || '') + '</td>';
                    tr += '<td>' + (row['Section'] || '') + '</td>';
                    tr += '<td>' + (row['Subsection'] || '') + '</td>';
                    tr += '<td>' + (row['Timing/Deadline'] || '') + '</td>';
                    tr += '<td>' + (row['Simple Description'] || '') + '</td>';
                    tr += '<td>' + (row['Specification'] || '') + '</td>';
                    tr += '<td>' + (row['Phase'] || '') + '</td>';
                    tr += '<td>' + (row['Responsible Party'] || '') + '</td>';
                    tr += '<td>' + (row['WSDOT Lead'] || '') + '</td>';
                    tr += '<td>' + (row['Notes'] || '') + '</td>';
                    tr += '</tr>';
                    tbody.append(tr);
                }});

                // Initialize DataTable with same settings as drill-down
                var allTable = $('#drilldown_table').DataTable({{
                    ordering: true,
                    paging: true,
                    searching: true,
                    search: {{
                        smart: true,
                        caseInsensitive: true
                    }},
                    order: [[3, 'asc']], // Sort by Subsection (column index 3) by default
                    pageLength: 25,
                    colReorder: true,
                    autoWidth: true,
                    scrollX: true,
                    responsive: false,
                    scrollCollapse: true,
                    dom: 'Bfrtip',
                    buttons: [
                        {{
                            extend: 'colvis',
                            text: 'Show/Hide Columns',
                            className: 'btn-secondary'
                        }}
                    ],
                    columnDefs: [
                        {{ width: '90px', targets: 0 }},
                        {{ width: '150px', targets: 1 }},
                        {{ width: '90px', targets: 2 }},
                        {{ width: '200px', targets: 3 }},
                        {{ width: '110px', targets: 4 }},
                        {{ width: '250px', targets: 5 }},
                        {{ width: '350px', targets: 6 }},
                        {{ width: '100px', targets: 7 }},
                        {{ width: '120px', targets: 8 }},
                        {{ width: '120px', targets: 9 }},
                        {{ width: '200px', targets: 10 }}
                    ],
                    initComplete: function() {{
                        var api = this.api();
                        // Default visible columns: Status, Section, Subsection, Timing/Deadline, Simple Description
                        var defaultVisible = [0, 2, 3, 4, 5];
                        api.columns().every(function(index) {{
                            this.visible(defaultVisible.includes(index));
                        }});
                    }}
                }});
            }} else {{
                // Show legend and instructions for chart tabs
                $('#chart-legend').show();
                $('#chart-instructions').show();

                // Move drilldown table back to original position
                $('#all-requirements-table-container').hide();
                if ($('#all-requirements-table-container #drilldown').length > 0) {{
                    $('body').append($('#drilldown'));
                }}

                // Reset table styling and hide drill-down table when switching to chart tabs
                $('#drilldown').css({{
                    'margin-top': '30px',
                    'padding': '0 30px'
                }});
                $('#drilldown_title').css({{
                    'margin-top': '20px',
                    'margin-bottom': '20px'
                }});
                $('#drilldown').hide();
            }}
        }}

        // Initialize everything when document is ready
        $(document).ready(function() {{
            // Generic function to handle chart drill-down
            function setupChartDrilldown(chartId, filterField, titlePrefix) {{
                var chart = document.getElementById(chartId);
                if (chart) {{
                    // Click on bars to filter by status
                    chart.on('plotly_click', function(data) {{
                        var point = data.points[0];
                        var filterValue = point.y;
                        var statusClicked = point.data.name; // "Completed", "In Progress", or "Not Started"

                        // Filter the data
                        var filteredData = originalData.filter(function(row) {{
                            var matchesFilter = row[filterField] === filterValue;
                            if (statusClicked === 'Completed') {{
                                return matchesFilter && row['Status'] === 'Complete';
                            }} else if (statusClicked === 'In Progress') {{
                                return matchesFilter && ['In Progress', 'Due', 'Past Due', 'Ongoing', 'Located'].includes(row['Status']);
                            }} else if (statusClicked === 'Not Started') {{
                                return matchesFilter && row['Status'] === 'Not Started';
                            }} else {{
                                return matchesFilter;
                            }}
                        }});

                        showDrilldownTable(filterValue, statusClicked, filteredData);
                    }});

                    // Click on y-axis labels to show all statuses
                    // Need to wait for Plotly to fully render
                    var attachLabelHandlers = function() {{
                        setTimeout(function() {{
                            var chartElement = document.getElementById(chartId);
                            if (chartElement) {{
                                var yaxisLabels = chartElement.querySelectorAll('.ytick text');
                                yaxisLabels.forEach(function(label) {{
                                    label.style.cursor = 'pointer';
                                    label.style.fontWeight = '500';
                                    // Remove existing listeners to prevent duplicates
                                    var newLabel = label.cloneNode(true);
                                    label.parentNode.replaceChild(newLabel, label);

                                    newLabel.addEventListener('click', function(e) {{
                                        var filterValue = this.textContent.trim();

                                        // Filter data for all statuses
                                        var filteredData = originalData.filter(function(row) {{
                                            return row[filterField] === filterValue;
                                        }});

                                        showDrilldownTable(filterValue, 'All Statuses', filteredData);
                                        e.stopPropagation();
                                        e.preventDefault();
                                    }}, true);
                                }});
                            }}
                        }}, 500);
                    }};

                    // Attach handlers initially and after any chart updates
                    attachLabelHandlers();
                    chart.on('plotly_relayout', attachLabelHandlers);
                }}
            }}

            // Function to display the unified drilldown table
            function showDrilldownTable(filterValue, statusText, filteredData) {{
                // Show the drilldown section
                $('#drilldown').show();
                $('#drilldown_title').text(filterValue + ' - ' + statusText + ' (' + filteredData.length + ' items)');

                // Destroy existing table if it exists
                if ($.fn.DataTable.isDataTable('#drilldown_table')) {{
                    $('#drilldown_table').DataTable().destroy();
                }}

                // Populate table
                var tbody = $('#drilldown_table tbody');
                tbody.empty();
                filteredData.forEach(function(row) {{
                    var tr = '<tr>';
                    tr += '<td>' + (row['Status'] || '') + '</td>';
                    tr += '<td>' + (row['Status Notes'] || '') + '</td>';
                    tr += '<td>' + (row['Section'] || '') + '</td>';
                    tr += '<td>' + (row['Subsection'] || '') + '</td>';
                    tr += '<td>' + (row['Timing/Deadline'] || '') + '</td>';
                    tr += '<td>' + (row['Simple Description'] || '') + '</td>';
                    tr += '<td>' + (row['Specification'] || '') + '</td>';
                    tr += '<td>' + (row['Phase'] || '') + '</td>';
                    tr += '<td>' + (row['Responsible Party'] || '') + '</td>';
                    tr += '<td>' + (row['WSDOT Lead'] || '') + '</td>';
                    tr += '<td>' + (row['Notes'] || '') + '</td>';
                    tr += '</tr>';
                    tbody.append(tr);
                }});

                // Initialize DataTable
                chartTable = $('#drilldown_table').DataTable({{
                    ordering: true,
                    paging: true,
                    searching: true,
                    search: {{
                        smart: true,
                        caseInsensitive: true
                    }},
                    order: [[3, 'asc']], // Sort by Subsection (column index 3) by default
                    pageLength: 25,
                    colReorder: true,
                    autoWidth: true,
                    scrollX: true,
                    responsive: false,
                    scrollCollapse: true,
                    orderCellsTop: true,
                    stateSave: false,
                    dom: 'Bfrtip',
                    buttons: [
                        {{
                            extend: 'colvis',
                            text: 'Show/Hide Columns',
                            className: 'btn-secondary'
                        }}
                    ],
                    columnDefs: [
                        {{ width: '90px', targets: 0 }},  // Status
                        {{ width: '150px', targets: 1 }}, // Status Notes
                        {{ width: '90px', targets: 2 }}, // Section
                        {{ width: '200px', targets: 3 }}, // Subsection
                        {{ width: '110px', targets: 4 }}, // Timing/Deadline
                        {{ width: '250px', targets: 5 }}, // Simple Description
                        {{ width: '350px', targets: 6 }}, // Specification
                        {{ width: '100px', targets: 7 }}, // Phase
                        {{ width: '120px', targets: 8 }}, // Responsible Party
                        {{ width: '120px', targets: 9 }}, // WSDOT Lead
                        {{ width: '200px', targets: 10 }}  // Notes
                    ],
                    initComplete: function() {{
                        var api = this.api();

                        // Default visible columns: 0-Status, 2-Section, 3-Subsection, 4-Timing/Deadline, 5-Simple Description
                        var defaultVisible = [0, 2, 3, 4, 5];

                        // Clear old localStorage and use defaults
                        localStorage.removeItem('chartTableColumns');

                        // Set default column visibility
                        api.columns().every(function(index) {{
                            this.visible(defaultVisible.includes(index));
                        }});

                        // Save column visibility on change
                        api.on('column-visibility.dt', function() {{
                            var visibility = [];
                            api.columns().every(function() {{
                                visibility.push(this.visible());
                            }});
                            localStorage.setItem('chartTableColumns', JSON.stringify(visibility));
                        }});
                    }}
                }});

                // Auto-scroll disabled to prevent interference with chart zoom interactions
            }}

            // Setup drill-down for all charts
            setupChartDrilldown('milestone_chart', 'Milestone', 'Milestone');
            setupChartDrilldown('party_chart', 'Responsible Party', 'Responsible Party');
            setupChartDrilldown('section_chart_col1', 'Section', 'Section');
            setupChartDrilldown('section_chart_col2', 'Section', 'Section');
            setupChartDrilldown('category_chart', 'Phase', 'Phase');
            setupChartDrilldown('deliverable_chart', 'Format', 'Format');

            // Handle window resize to adjust DataTable columns and Plotly charts
            var resizeTimer;
            $(window).on('resize', function() {{
                clearTimeout(resizeTimer);
                resizeTimer = setTimeout(function() {{
                    // Adjust DataTables
                    if ($.fn.DataTable.isDataTable('#drilldown_table')) {{
                        $('#drilldown_table').DataTable().columns.adjust().draw();
                    }}

                    // Relayout Plotly charts
                    var chartIds = ['milestone_chart', 'party_chart', 'section_chart_col1', 'section_chart_col2',
                                   'category_chart', 'deliverable_chart'];
                    chartIds.forEach(function(chartId) {{
                        var chartElement = document.getElementById(chartId);
                        if (chartElement) {{
                            Plotly.Plots.resize(chartElement);
                        }}
                    }});
                }}, 250);
            }});
        }});
    </script>

    <footer style="position: fixed; bottom: 0; left: 0; right: 0; padding: 15px; background: #1e3a8a; color: white; text-align: center; font-size: 14px; z-index: 1000; box-shadow: 0 -2px 10px rgba(0,0,0,0.1);">
        <a href="mailto:zach.archer@consultant.wsdot.wa.gov" style="color: #93c5fd; text-decoration: none; margin: 0 10px;">zach.archer@consultant.wsdot.wa.gov</a> |
        <a href="mailto:lisa.danks@consultant.wsdot.wa.gov" style="color: #93c5fd; text-decoration: none; margin: 0 10px;">lisa.danks@consultant.wsdot.wa.gov</a> |
        <a href="mailto:kristin.wells@consultant.wsdot.wa.gov" style="color: #93c5fd; text-decoration: none; margin: 0 10px;">kristin.wells@consultant.wsdot.wa.gov</a>
    </footer>
    <div style="height: 60px;"></div> <!-- Spacer to prevent content from being hidden under fixed footer -->
</body>
</html>
"""

# Combine everything
full_html = html_header + charts_html + html_footer

# Write to file
output_file = '/Users/z/Desktop/montlake_closeout.html'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(full_html)

print(f"✅ Enhanced dashboard created: {output_file}")
print(f"\n📊 Dashboard Statistics:")
print(f"   Total Requirements: {total_items}")
print(f"   Completed: {completed_items} ({overall_completion:.1f}%)")
print(f"   In Progress: {in_progress_items} ({(in_progress_items/total_items*100):.1f}%)")
print(f"   Not Started: {not_started_items} ({(not_started_items/total_items*100):.1f}%)")
print(f"\n📊 Charts Available:")
print(f"   - Milestones, Responsible Party, Sections, Phase, Format")
print(f"   - All charts have interactive drill-down capability")
