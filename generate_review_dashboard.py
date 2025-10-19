#!/usr/bin/env python3
"""
Montlake Document Review Dashboard Generator

Generates an interactive HTML dashboard for tracking contract document reviews
Output: review-dashboard.html
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from datetime import datetime
import json

print("📊 Generating Document Review Dashboard...")
print()

# Read tracker data
tracker_file = 'contract_documents_complete_tracker.csv'
try:
    df = pd.read_csv(tracker_file, encoding='utf-8-sig')
except FileNotFoundError:
    print(f"❌ Error: {tracker_file} not found")
    print("   Make sure you're in the montlake-closeout directory")
    exit(1)

print(f"✅ Loaded {len(df)} documents from tracker")

# Clean up data
df['Review_Status'] = df['Review_Status'].fillna('Not Started')
df['Notes'] = df['Notes'].fillna('')
df['Closeout_Requirements_Found'] = df['Closeout_Requirements_Found'].fillna('')
df['Follow_Up_Required'] = df['Follow_Up_Required'].fillna('')

# Calculate metrics
total_docs = len(df)
reviewed = len(df[df['Review_Status'] == 'Reviewed'])
in_progress = len(df[df['Review_Status'] == 'In Progress'])
not_started = len(df[df['Review_Status'] == 'Not Started'])
na = len(df[df['Review_Status'] == 'N/A'])

pct_reviewed = (reviewed / total_docs * 100) if total_docs > 0 else 0
pct_in_progress = (in_progress / total_docs * 100) if total_docs > 0 else 0

# Requirements found
reqs_found = df[df['Closeout_Requirements_Found'] != '']
total_requirements = len(reqs_found)

# Follow-ups
follow_ups = df[df['Follow_Up_Required'].str.upper() == 'YES'] if 'Follow_Up_Required' in df.columns else pd.DataFrame()

print(f"✅ Progress: {reviewed}/{total_docs} ({pct_reviewed:.1f}%)")
print(f"✅ Requirements Found: {total_requirements}")
print()

# Create priority breakdown
priority_stats = df.groupby('Priority').agg({
    'Review_Status': lambda x: (x == 'Reviewed').sum()
}).reset_index()
priority_stats.columns = ['Priority', 'Reviewed']

# Add totals
for priority in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
    if priority not in priority_stats['Priority'].values:
        priority_stats = pd.concat([priority_stats, pd.DataFrame({'Priority': [priority], 'Reviewed': [0]})], ignore_index=True)

priority_totals = df.groupby('Priority').size().reset_index(name='Total')
priority_stats = priority_stats.merge(priority_totals, on='Priority')
priority_stats['Pct'] = (priority_stats['Reviewed'] / priority_stats['Total'] * 100).round(1)

# Category breakdown
category_stats = df.groupby('Category').agg({
    'Review_Status': lambda x: (x == 'Reviewed').sum()
}).reset_index()
category_stats.columns = ['Category', 'Reviewed']
category_totals = df.groupby('Category').size().reset_index(name='Total')
category_stats = category_stats.merge(category_totals, on='Category')
category_stats['Pct'] = (category_stats['Reviewed'] / category_stats['Total'] * 100).round(1)
category_stats = category_stats.sort_values('Total', ascending=False)

print("🎨 Creating charts...")

# Plotly config
plotly_config = {
    'displayModeBar': True,
    'displaylogo': False,
    'modeBarButtonsToRemove': ['lasso2d', 'select2d']
}

# CHART 1: Overall Progress Gauge
gauge_fig = go.Figure(go.Indicator(
    mode="gauge+number+delta",
    value=pct_reviewed,
    title={'text': "Overall Progress", 'font': {'size': 24}},
    delta={'reference': 0},
    gauge={
        'axis': {'range': [None, 100]},
        'bar': {'color': "#059669"},
        'steps': [
            {'range': [0, 25], 'color': "#fee2e2"},
            {'range': [25, 50], 'color': "#fef3c7"},
            {'range': [50, 75], 'color': "#dbeafe"},
            {'range': [75, 100], 'color': "#d1fae5"}
        ],
        'threshold': {
            'line': {'color': "red", 'width': 4},
            'thickness': 0.75,
            'value': 90
        }
    }
))
gauge_fig.update_layout(height=300, margin=dict(l=20, r=20, t=60, b=20))

# CHART 2: Priority Breakdown
priority_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
priority_stats['Order'] = priority_stats['Priority'].map(priority_order)
priority_stats = priority_stats.sort_values('Order')

priority_fig = go.Figure()
priority_fig.add_trace(go.Bar(
    y=priority_stats['Priority'],
    x=priority_stats['Reviewed'],
    name='Reviewed',
    orientation='h',
    marker=dict(color='#059669'),
    text=priority_stats['Reviewed'],
    textposition='inside'
))
priority_fig.add_trace(go.Bar(
    y=priority_stats['Priority'],
    x=priority_stats['Total'] - priority_stats['Reviewed'],
    name='Remaining',
    orientation='h',
    marker=dict(color='#e5e7eb'),
    text=priority_stats['Total'] - priority_stats['Reviewed'],
    textposition='inside'
))
priority_fig.update_layout(
    barmode='stack',
    title='Progress by Priority',
    height=300,
    xaxis_title='Documents',
    yaxis_title='',
    showlegend=True,
    margin=dict(l=20, r=20, t=60, b=40)
)

# CHART 3: Category Breakdown (Top 10)
top_categories = category_stats.head(10)
category_fig = go.Figure(go.Bar(
    x=top_categories['Category'],
    y=top_categories['Pct'],
    text=top_categories.apply(lambda x: f"{x['Reviewed']}/{x['Total']}", axis=1),
    textposition='outside',
    marker=dict(color=top_categories['Pct'], colorscale='Greens', showscale=False)
))
category_fig.update_layout(
    title='Top 10 Categories Progress (%)',
    height=400,
    xaxis_title='',
    yaxis_title='% Reviewed',
    margin=dict(l=20, r=20, t=60, b=120),
    xaxis={'tickangle': -45}
)

# CHART 4: Status Pie Chart
status_data = pd.DataFrame({
    'Status': ['Reviewed', 'In Progress', 'Not Started', 'N/A'],
    'Count': [reviewed, in_progress, not_started, na]
})
status_data = status_data[status_data['Count'] > 0]

status_fig = go.Figure(go.Pie(
    labels=status_data['Status'],
    values=status_data['Count'],
    marker=dict(colors=['#059669', '#fbbf24', '#e5e7eb', '#9ca3af']),
    textinfo='label+percent',
    hovertemplate='%{label}<br>%{value} documents<br>%{percent}<extra></extra>'
))
status_fig.update_layout(
    title='Document Status Distribution',
    height=350,
    margin=dict(l=20, r=20, t=60, b=20)
)

print("✅ Charts created")
print()

# Prepare data for JavaScript table
table_data = []
for _, row in df.iterrows():
    table_data.append({
        'Priority': row['Priority'],
        'Status': row['Review_Status'],
        'Category': row['Category'],
        'Appendix_Number': str(row['Appendix_Number']) if pd.notna(row['Appendix_Number']) else '',
        'Filename': row['Filename'],
        'Requirements': row['Closeout_Requirements_Found'],
        'Notes': row['Notes'],
        'Reviewer': str(row['Reviewer']) if pd.notna(row['Reviewer']) else '',
        'Review_Date': str(row['Review_Date']) if pd.notna(row['Review_Date']) else '',
        'Follow_Up': str(row['Follow_Up_Required']) if pd.notna(row['Follow_Up_Required']) else '',
        'Full_Path': str(row['Full_Path']) if pd.notna(row['Full_Path']) else ''
    })

table_data_json = json.dumps(table_data)
plotly_config_json = json.dumps(plotly_config)

# Generate HTML
html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Montlake Document Review Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <link rel="stylesheet" href="https://cdn.datatables.net/1.13.7/css/jquery.dataTables.min.css">
    <script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
    <script src="https://cdn.datatables.net/1.13.7/js/jquery.dataTables.min.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
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
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .metric-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .metric-value {{
            font-size: 32px;
            font-weight: 700;
            margin: 10px 0;
        }}
        .metric-label {{
            color: #6b7280;
            font-size: 14px;
        }}
        .chart-container {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        .grid-2 {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }}
        .table-container {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        .status-reviewed {{ color: #059669; font-weight: 600; }}
        .status-in-progress {{ color: #f59e0b; font-weight: 600; }}
        .status-not-started {{ color: #6b7280; }}
        .status-na {{ color: #9ca3af; }}
        .priority-critical {{ color: #dc2626; font-weight: 700; }}
        .priority-high {{ color: #f97316; font-weight: 600; }}
        .priority-medium {{ color: #eab308; }}
        .priority-low {{ color: #6b7280; }}
        h2 {{
            color: #1e3a8a;
            margin-top: 0;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            color: #6b7280;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Montlake Document Review Dashboard</h1>
        <p>Contract Documents Closeout Review Tracker</p>
        <p>Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
    </div>

    <div class="container">
        <!-- Key Metrics -->
        <div class="metrics">
            <div class="metric-card">
                <div class="metric-label">Total Documents</div>
                <div class="metric-value">{total_docs:,}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Reviewed</div>
                <div class="metric-value" style="color: #059669;">{reviewed}</div>
                <div class="metric-label">{pct_reviewed:.1f}%</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">In Progress</div>
                <div class="metric-value" style="color: #f59e0b;">{in_progress}</div>
                <div class="metric-label">{pct_in_progress:.1f}%</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Requirements Found</div>
                <div class="metric-value" style="color: #3b82f6;">{total_requirements}</div>
            </div>
        </div>

        <!-- Progress Gauge and Status Pie -->
        <div class="grid-2">
            <div class="chart-container">
                <div id="gauge-chart"></div>
            </div>
            <div class="chart-container">
                <div id="status-chart"></div>
            </div>
        </div>

        <!-- Priority and Category Charts -->
        <div class="chart-container">
            <div id="priority-chart"></div>
        </div>

        <div class="chart-container">
            <div id="category-chart"></div>
        </div>

        <!-- Document Table -->
        <div class="table-container">
            <h2>All Documents</h2>
            <table id="documents-table" class="display" style="width:100%">
                <thead>
                    <tr>
                        <th>Priority</th>
                        <th>Status</th>
                        <th>Category</th>
                        <th>ID/Number</th>
                        <th>Filename</th>
                        <th>Requirements</th>
                        <th>Notes</th>
                        <th>Reviewer</th>
                        <th>Date</th>
                        <th>Follow-Up</th>
                        <th>File Path</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
        </div>
    </div>

    <div class="footer">
        Montlake Bridge Replacement Project - Document Review Dashboard<br>
        Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
    </div>

    <script>
        // Render charts
        var plotlyConfig = {plotly_config_json};
        var gaugeConfig = {gauge_fig.to_json()};
        Plotly.newPlot('gauge-chart', gaugeConfig.data, gaugeConfig.layout, plotlyConfig);

        var statusConfig = {status_fig.to_json()};
        Plotly.newPlot('status-chart', statusConfig.data, statusConfig.layout, plotlyConfig);

        var priorityConfig = {priority_fig.to_json()};
        Plotly.newPlot('priority-chart', priorityConfig.data, priorityConfig.layout, plotlyConfig);

        var categoryConfig = {category_fig.to_json()};
        Plotly.newPlot('category-chart', categoryConfig.data, categoryConfig.layout, plotlyConfig);

        // Initialize DataTable
        var tableData = {table_data_json};

        $(document).ready(function() {{
            var table = $('#documents-table').DataTable({{
                data: tableData,
                columns: [
                    {{
                        data: 'Priority',
                        render: function(data) {{
                            var className = 'priority-' + data.toLowerCase();
                            return '<span class="' + className + '">' + data + '</span>';
                        }}
                    }},
                    {{
                        data: 'Status',
                        render: function(data) {{
                            var className = 'status-' + data.toLowerCase().replace(' ', '-');
                            return '<span class="' + className + '">' + data + '</span>';
                        }}
                    }},
                    {{ data: 'Category' }},
                    {{ data: 'Appendix_Number' }},
                    {{ data: 'Filename' }},
                    {{ data: 'Requirements' }},
                    {{ data: 'Notes' }},
                    {{ data: 'Reviewer' }},
                    {{ data: 'Review_Date' }},
                    {{ data: 'Follow_Up' }},
                    {{
                        data: 'Full_Path',
                        render: function(data) {{
                            if (data && data.length > 60) {{
                                return '<span title="' + data + '">' + data.substring(0, 60) + '...</span>';
                            }}
                            return data;
                        }}
                    }}
                ],
                order: [[0, 'asc'], [1, 'asc']],
                pageLength: 25,
                responsive: true
            }});
        }});
    </script>
</body>
</html>
"""

# Write HTML file
output_file = 'review-dashboard.html'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"✅ Dashboard created: {output_file}")
print()
print("📊 Summary:")
print(f"   Total Documents: {total_docs}")
print(f"   Reviewed: {reviewed} ({pct_reviewed:.1f}%)")
print(f"   In Progress: {in_progress}")
print(f"   Requirements Found: {total_requirements}")
print()
