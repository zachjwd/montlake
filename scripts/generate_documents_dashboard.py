#!/usr/bin/env python3
"""
Documents Dashboard Generator
Shows all required deliverables and their review status
"""

import pandas as pd
from datetime import datetime

print("📊 Generating Documents Dashboard...")
print()

# Read documents tracker
df = pd.read_csv('data/documents_tracker.csv')
print(f"✅ Loaded {len(df)} documents")

# Calculate basic stats
total = len(df)
reviewed = len(df[df['Review_Status'] == 'Reviewed'])
in_progress = len(df[df['Review_Status'] == 'In Progress'])
not_started = len(df[df['Review_Status'] == 'Not Started'])

# Calculate section-weighted progress
sections = df['Contract_Section'].unique()
sections_complete = 0
section_progress_sum = 0

for section in sections:
    section_docs = df[df['Contract_Section'] == section]
    section_total = len(section_docs)
    section_reviewed = len(section_docs[section_docs['Review_Status'] == 'Reviewed'])
    section_pct = section_reviewed / section_total if section_total > 0 else 0
    section_progress_sum += section_pct

    if section_reviewed == section_total:
        sections_complete += 1

overall_section_weighted = (section_progress_sum / len(sections)) * 100

# Format timestamp with linked AM/PM
now = datetime.now()
time_part = now.strftime('%B %d, %Y at %I:%M')
am_pm = now.strftime('%p')

# Generate HTML
html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Montlake Closeout Documents Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: #f5f7fa;
            padding: 20px;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .header h1 {{
            font-size: 32px;
            margin-bottom: 8px;
        }}
        .header p {{
            opacity: 0.9;
            font-size: 14px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .stat-card .label {{
            color: #64748b;
            font-size: 14px;
            margin-bottom: 8px;
        }}
        .stat-card .value {{
            font-size: 32px;
            font-weight: bold;
            color: #1e293b;
        }}
        .stat-card .detail {{
            color: #64748b;
            font-size: 13px;
            margin-top: 4px;
        }}
        .progress-bar {{
            height: 8px;
            background: #e2e8f0;
            border-radius: 4px;
            margin-top: 12px;
            overflow: hidden;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #10b981 0%, #059669 100%);
            transition: width 0.3s ease;
        }}
        .section {{
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .section-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            cursor: pointer;
            user-select: none;
            border-radius: 6px;
            transition: background 0.2s;
        }}
        .section-header:hover {{
            background: #f8fafc;
        }}
        .section-title {{
            font-size: 18px;
            font-weight: 600;
            color: #1e293b;
        }}
        .section-stats {{
            display: flex;
            gap: 20px;
            align-items: center;
            font-size: 14px;
            color: #64748b;
        }}
        .section-content {{
            display: none;
            padding: 0 15px 15px;
        }}
        .section-content.active {{
            display: block;
        }}
        .category-group {{
            margin: 15px 0;
            padding: 12px;
            background: #f8fafc;
            border-radius: 6px;
        }}
        .category-header {{
            font-weight: 600;
            color: #475569;
            margin-bottom: 10px;
            font-size: 14px;
        }}
        .doc-list {{
            list-style: none;
        }}
        .doc-item {{
            padding: 10px;
            margin: 4px 0;
            background: white;
            border-radius: 4px;
            border-left: 3px solid #e2e8f0;
            font-size: 13px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .doc-item.reviewed {{
            border-left-color: #10b981;
        }}
        .doc-item.needs-review {{
            border-left-color: #f59e0b;
        }}
        .doc-number {{
            font-weight: 600;
            color: #6366f1;
            margin-right: 8px;
        }}
        .doc-name {{
            flex: 1;
            color: #1e293b;
        }}
        .status-badge {{
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
        }}
        .status-badge.reviewed {{
            background: #d1fae5;
            color: #065f46;
        }}
        .status-badge.needs-review {{
            background: #fef3c7;
            color: #92400e;
        }}
        .expand-icon {{
            transition: transform 0.3s;
            color: #94a3b8;
        }}
        .expand-icon.active {{
            transform: rotate(90deg);
        }}
        .file-count {{
            font-size: 11px;
            color: #64748b;
            margin-left: 8px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Montlake Closeout Review Dashboard</h1>
            <p>Tracking {total} Documents | Updated {time_part} <a href="closeout_dashboard.html" style="color:inherit; text-decoration:none; cursor:pointer;" title="Go to Closeout Dashboard">{am_pm}</a></p>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="label">Overall Progress (Section-Weighted)</div>
                <div class="value">{overall_section_weighted:.1f}%</div>
                <div class="detail">{sections_complete} of {len(sections)} sections complete</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {overall_section_weighted:.1f}%"></div>
                </div>
            </div>

            <div class="stat-card">
                <div class="label">Documents Reviewed</div>
                <div class="value">{reviewed}/{total}</div>
                <div class="detail">{reviewed/total*100:.1f}% of all documents</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {reviewed/total*100:.1f}%"></div>
                </div>
            </div>

            <div class="stat-card">
                <div class="label">Review Status</div>
                <div class="value">{not_started}</div>
                <div class="detail">Not Started | {in_progress} In Progress | {reviewed} Reviewed</div>
            </div>
        </div>

        <div class="section">
            <h2 style="margin-bottom: 20px; color: #1e293b;">Contract Sections</h2>
"""

# Group by contract section
for section in sorted(df['Contract_Section'].unique()):
    section_docs = df[df['Contract_Section'] == section]
    section_total = len(section_docs)
    section_reviewed = len(section_docs[section_docs['Review_Status'] == 'Reviewed'])
    section_not_reviewed = section_total - section_reviewed
    section_pct = (section_reviewed / section_total * 100) if section_total > 0 else 0

    section_id = section.replace('.', '').replace(' ', '-').replace('(', '').replace(')', '')

    html += f"""
            <div class="section-item">
                <div class="section-header" onclick="toggleSection('{section_id}')">
                    <div>
                        <div class="section-title">{section}</div>
                    </div>
                    <div class="section-stats">
                        <span>{section_reviewed}/{section_total} reviewed ({section_pct:.0f}%)</span>
                        <span>|</span>
                        <span>{section_not_reviewed} not reviewed</span>
                        <span class="expand-icon" id="icon-{section_id}">▶</span>
                    </div>
                </div>
                <div class="section-content" id="content-{section_id}">
"""

    # Group by category within section
    # Fill NaN categories with "Standard Documents"
    section_docs_copy = section_docs.copy()
    section_docs_copy['Category'] = section_docs_copy['Category'].fillna('Standard Documents')

    categories = section_docs_copy['Category'].unique()
    for category in sorted(categories):
        cat_docs = section_docs_copy[section_docs_copy['Category'] == category]

        if len(cat_docs) > 0:
            html += f"""
                    <div class="category-group">
                        <div class="category-header">{category} ({len(cat_docs)} deliverables)</div>
                        <ul class="doc-list">
"""

            for _, doc in cat_docs.iterrows():
                review_status = doc['Review_Status']
                status_class = 'reviewed' if review_status == 'Reviewed' else 'needs-review'
                doc_name = doc['Document_Name']
                doc_num = doc['Doc_Number']

                html += f"""
                            <li class="doc-item {status_class}">
                                <div style="display: flex; align-items: center; flex: 1;">
                                    <span class="doc-number">[{doc_num}]</span>
                                    <span class="doc-name">{doc_name}</span>
                                </div>
                                <span class="status-badge {status_class}">{review_status}</span>
                            </li>
"""

            html += """
                        </ul>
                    </div>
"""

    html += """
                </div>
            </div>
"""

html += """
        </div>
    </div>

    <script>
        function toggleSection(sectionId) {
            const content = document.getElementById('content-' + sectionId);
            const icon = document.getElementById('icon-' + sectionId);

            if (content.classList.contains('active')) {
                content.classList.remove('active');
                icon.classList.remove('active');
            } else {
                content.classList.add('active');
                icon.classList.add('active');
            }
        }
    </script>
</body>
</html>
"""

# Write HTML file
output_file = 'dashboard/documents_dashboard.html'
with open(output_file, 'w') as f:
    f.write(html)

print(f"✅ Dashboard generated: {output_file}")
print()
print(f"📊 Overall Progress: {overall_section_weighted:.1f}% (section-weighted)")
print(f"📋 Documents: {reviewed}/{total} reviewed ({reviewed/total*100:.1f}%)")
print(f"✅ Reviewed: {reviewed} | 🔄 In Progress: {in_progress} | 📋 Not Started: {not_started}")
print()
