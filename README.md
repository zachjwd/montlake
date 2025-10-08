# Montlake Closeout Dashboard

Interactive dashboard for tracking Montlake project closeout requirements.

Live site: https://zachjwd.github.io/montlake/

## Updating the Dashboard

The dashboard is generated from the CSV data file using a Python script.

### Steps to update:

1. **Navigate to the repository directory:**
   ```bash
   cd /Users/z/Desktop/montlake-closeout
   ```

2. **Run the generator script:**
   ```bash
   python3 closeout_dashboard_v3.py
   ```
   This creates `/Users/z/Desktop/montlake_closeout.html`

3. **Copy to index.html for GitHub Pages:**
   ```bash
   cp /Users/z/Desktop/montlake_closeout.html index.html
   ```

4. **Commit and push to GitHub:**
   ```bash
   git add -A
   git commit -m "Update dashboard"
   git push
   ```

### Important Notes

- The script **must be run from the `/Users/z/Desktop/montlake-closeout/` directory** for the copy command to work correctly
- Output file is always written to `/Users/z/Desktop/montlake_closeout.html`
- GitHub Pages serves from `index.html` in the repository root
- Data source: `/Users/z/Desktop/Montlake - Closeout.csv`

## Dashboard Features

- **6 interactive views:** Milestones, Sections (split view), Categories, Deliverable Types, Responsibility, All Requirements
- **Drill-down functionality:** Click any chart segment to filter requirements
- **Column visibility controls:** Show/hide table columns as needed
- **Status tracking:** Complete, In Progress, Not Started
- **Persistent settings:** Column visibility saved in browser
