#!/usr/bin/env python3
"""
Documents Dashboard Generator
Shows all required deliverables and their review status
"""

import pandas as pd
import re
from datetime import datetime

def extract_appendix_code(file_path):
    """
    Extract appendix code from file path.
    Examples:
      .../Appendix A1/... → A1
      .../Appendix D34/Appendix D34.A/... → D34.A
      .../Appendix A4/Appendix A4.1.../... → A4.1
    """
    if pd.isna(file_path):
        return None

    # Find all "Appendix XX" patterns in the path
    matches = re.findall(r'Appendix ([A-Z][A-Z0-9.-]+)', str(file_path))

    if not matches:
        return None

    # Return the most specific (longest) appendix code found
    return max(matches, key=len)

print("📊 Generating Documents Dashboard...")
print()

# Read documents tracker
df = pd.read_csv('data/documents_tracker.csv')
print(f"✅ Loaded {len(df)} documents")

# Standardize Review_Status capitalization (handle "In progress" vs "In Progress")
df['Review_Status'] = df['Review_Status'].str.strip()
df.loc[df['Review_Status'].str.lower() == 'in progress', 'Review_Status'] = 'In Progress'

# Extract appendix codes from file paths
df['Appendix_Code'] = df['File_Path'].apply(extract_appendix_code)

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
            background: #f5f5f5;
            margin: 0;
            padding: 0;
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
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
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
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
            user-select: none;
            padding: 8px 10px;
            border-radius: 6px;
            transition: background 0.2s;
        }}
        .category-header:hover {{
            background: #f1f5f9;
        }}
        .category-content {{
            display: none;
        }}
        .category-content.active {{
            display: block;
        }}
        .appendix-group {{
            margin: 8px 0;
            background: white;
            border-radius: 4px;
            border: 1px solid #e2e8f0;
        }}
        .appendix-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 12px;
            cursor: pointer;
            user-select: none;
            transition: background 0.2s;
            border-radius: 4px;
        }}
        .appendix-header:hover {{
            background: #f8fafc;
        }}
        .appendix-title {{
            font-weight: 600;
            color: #1e293b;
            font-size: 13px;
            flex: 1;
        }}
        .appendix-content {{
            display: none;
            padding: 10px 12px 12px;
            border-top: 1px solid #e2e8f0;
        }}
        .appendix-content.active {{
            display: block;
        }}
        .appendix-details {{
            font-size: 12px;
            color: #64748b;
            line-height: 1.6;
        }}
        .appendix-details strong {{
            color: #475569;
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
            flex-direction: column;
            gap: 8px;
        }}
        .doc-item-header {{
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
        .doc-notes {{
            font-size: 12px;
            color: #64748b;
            font-style: italic;
            padding-left: 20px;
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
    <div class="header">
        <h1>MONTLAKE CLOSEOUT - CONTRACT DOCUMENTS REVIEW</h1>
        <p>Tracking {total} Documents | Updated {time_part} <a href="index.html" style="color:inherit; text-decoration:none; cursor:pointer;" title="Go to Closeout Dashboard">{am_pm}</a></p>
    </div>

    <div class="container">
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
            <h2 style="margin-bottom: 20px; color: #1e293b;">Contract Documents</h2>
"""

# Group by contract section
for section in sorted(df['Contract_Section'].unique()):
    section_docs = df[df['Contract_Section'] == section]
    section_total = len(section_docs)
    section_reviewed = len(section_docs[section_docs['Review_Status'] == 'Reviewed'])
    section_not_reviewed = section_total - section_reviewed
    section_pct = (section_reviewed / section_total * 100) if section_total > 0 else 0

    # Build a safe section id: no spaces, parentheses, or apostrophes
    section_id = (
        section
        .replace("'", '')
        .replace('.', '')
        .replace(' ', '-')
        .replace('(', '')
        .replace(')', '')
    )

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
            # Create a safe id for the category within this section
            cat_key = re.sub(r'[^A-Za-z0-9\-]', '', category.replace(' ', '-').replace('(', '').replace(')', ''))
            category_id = f"{section_id}-{cat_key}"
            html += f"""
                    <div class="category-group">
                        <div class="category-header" onclick="toggleCategory('{category_id}')">
                            <span>{category} ({len(cat_docs)} deliverables)</span>
                            <span class="expand-icon" id="icon-{category_id}">▶</span>
                        </div>
                        <div class="category-content" id="content-{category_id}">
"""

            # Group by appendix code within category
            appendix_groups = cat_docs.groupby('Appendix_Code', dropna=False)

            for appendix_code, appendix_docs in appendix_groups:
                # For documents without appendix code (Standard docs), show directly
                if pd.isna(appendix_code):
                    html += """
                        <ul class="doc-list">
"""
                    for _, doc in appendix_docs.iterrows():
                        review_status = doc['Review_Status']
                        status_class = 'reviewed' if review_status == 'Reviewed' else 'needs-review'
                        doc_name = doc['Document_Name']
                        doc_num = doc['Doc_Number']
                        notes = doc.get('Notes', '')

                        html += f"""
                            <li class="doc-item {status_class}">
                                <div class="doc-item-header">
                                    <div style="display: flex; align-items: center; flex: 1;">
                                        <span class="doc-number">[{doc_num}]</span>
                                        <span class="doc-name">{doc_name}</span>
                                    </div>
                                    <span class="status-badge {status_class}">{review_status}</span>
                                </div>"""

                        if notes and str(notes).strip():
                            html += f"""
                                <div class="doc-notes">{notes}</div>"""

                        html += """
                            </li>
"""
                    html += """
                        </ul>
"""
                else:
                    # For appendices, create collapsible groups
                    appendix_id = f"{section_id}-{category.replace(' ', '-').replace('(', '').replace(')', '')}-{appendix_code.replace('.', '-')}"

                    # Get the first doc for the appendix title
                    first_doc = appendix_docs.iloc[0]
                    doc_name = first_doc['Document_Name']
                    review_status = first_doc['Review_Status']
                    status_class = 'reviewed' if review_status == 'Reviewed' else 'needs-review'

                    html += f"""
                        <div class="appendix-group">
                            <div class="appendix-header" onclick="toggleAppendix('{appendix_id}')">
                                <span class="appendix-title">Appendix {appendix_code} - {doc_name}</span>
                                <div style="display: flex; align-items: center; gap: 10px;">
                                    <span class="status-badge {status_class}">{review_status}</span>
                                    <span class="expand-icon" id="icon-{appendix_id}">▶</span>
                                </div>
                            </div>
                            <div class="appendix-content" id="content-{appendix_id}">
                                <div class="appendix-details">
"""

                    # Show details for all docs in this appendix
                    for idx, doc in appendix_docs.iterrows():
                        rep_file = doc.get('Representative_File', '')
                        notes = doc.get('Notes', '')

                        if pd.notna(rep_file) and str(rep_file).strip():
                            html += f"""
                                    <div style="margin-bottom: 8px;">
                                        <strong>File:</strong> {rep_file}
                                    </div>
"""

                        if pd.notna(notes) and str(notes).strip():
                            html += f"""
                                    <div style="margin-bottom: 8px;">
                                        <strong>Notes:</strong> {notes}
                                    </div>
"""

                    html += """
                                </div>
                            </div>
                        </div>
"""

            html += """
                        </div>
                    </div>
"""

    html += """
                </div>
            </div>
"""

html += """
        </div>
    </div>

    <footer style="position: fixed; bottom: 0; left: 0; right: 0; padding: 15px; background: #1e3a8a; color: white; text-align: center; font-size: 14px; z-index: 1000; box-shadow: 0 -2px 10px rgba(0,0,0,0.1);">
        <a href="mailto:zach.archer@consultant.wsdot.wa.gov" style="color: #93c5fd; text-decoration: none; margin: 0 10px;">zach.archer@consultant.wsdot.wa.gov</a> |
        <a href="mailto:lisa.danks@consultant.wsdot.wa.gov" style="color: #93c5fd; text-decoration: none; margin: 0 10px;">lisa.danks@consultant.wsdot.wa.gov</a> |
        <a href="mailto:kristin.wells@consultant.wsdot.wa.gov" style="color: #93c5fd; text-decoration: none; margin: 0 10px;">kristin.wells@consultant.wsdot.wa.gov</a>
    </footer>
    <div style="height: 60px;"></div>

    <script>
        function toggleCategory(categoryId) {
            const content = document.getElementById('content-' + categoryId);
            const icon = document.getElementById('icon-' + categoryId);
            if (!content || !icon) return;
            if (content.classList.contains('active')) {
                content.classList.remove('active');
                icon.classList.remove('active');
            } else {
                content.classList.add('active');
                icon.classList.add('active');
            }
        }

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

        function toggleAppendix(appendixId) {
            const content = document.getElementById('content-' + appendixId);
            const icon = document.getElementById('icon-' + appendixId);

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
output_file = 'contractdocs.html'
with open(output_file, 'w') as f:
    f.write(html)

print(f"✅ Dashboard generated: {output_file}")
print()
print(f"📊 Overall Progress: {overall_section_weighted:.1f}% (section-weighted)")
print(f"📋 Documents: {reviewed}/{total} reviewed ({reviewed/total*100:.1f}%)")
print(f"✅ Reviewed: {reviewed} | 🔄 In Progress: {in_progress} | 📋 Not Started: {not_started}")
print()
