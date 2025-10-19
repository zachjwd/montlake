# Montlake Closeout Dashboards

Interactive dashboards for tracking Montlake Bridge Replacement Project closeout activities.

**Live Dashboards:**
- **Closeout Requirements:** https://zachjwd.github.io/montlake/
- **Document Review:** https://zachjwd.github.io/montlake/review-dashboard.html

---

## Quick Start

Update both dashboards with a single command:

```bash
update-montlake
```

This will:
1. Generate closeout requirements dashboard
2. Generate document review dashboard
3. Commit changes to Git
4. Push to GitHub (dashboards update in 1-2 minutes)

---

## Project Structure

```
montlake-closeout/
├── update_dashboard.sh          # Main update script
├── index.html                   # Closeout dashboard (GitHub Pages)
├── review-dashboard.html        # Document review dashboard (GitHub Pages)
│
├── data/
│   ├── current_closeout.csv                      # Closeout requirements tracking
│   ├── contract_documents_complete_tracker.csv   # Document review tracking
│   └── inventories/
│       ├── all_change_orders_inventory.csv       # Change orders catalog
│       ├── appendices_inventory.csv              # Appendices catalog
│       └── appendices_summary.txt                # Appendices summary
│
├── scripts/
│   ├── closeout_dashboard_v3.py           # Closeout dashboard generator
│   ├── generate_review_dashboard.py       # Review dashboard generator
│   └── utilities/
│       ├── scan_appendices.py             # Scan OneDrive for appendices
│       ├── scan_all_change_orders.py      # Scan OneDrive for change orders
│       ├── create_final_complete_tracker.py  # Generate complete document tracker
│       ├── review_progress.py             # Show review progress stats
│       └── view_versions.sh               # View git version history
│
└── docs/
    ├── OPTIMAL_REVIEW_WORKFLOW.md         # Document review workflow guide
    ├── REVIEW_STATUS_PRESENTATION.md      # How to present review status
    ├── CONTRACT_DOCUMENTS_FOUND.md        # Complete contract documents catalog
    ├── APPENDIX_REVIEW_GUIDE.md           # Guide for reviewing appendices
    └── DASHBOARD_USAGE.md                 # Dashboard usage instructions
```

---

## Dashboards

### 1. Closeout Requirements Dashboard

**URL:** https://zachjwd.github.io/montlake/

**Tracks:** 257 closeout requirements from contract documents

**Features:**
- Interactive charts by milestone, responsible party, section, phase
- Drill-down capability - click any chart to filter
- Status tracking: Complete, In Progress, Not Started
- Column visibility controls
- Persistent settings

**Data Source:** `data/current_closeout.csv`

### 2. Document Review Dashboard

**URL:** https://zachjwd.github.io/montlake/review-dashboard.html

**Tracks:** 1,261 contract documents for closeout requirements

**Features:**
- Overall progress gauge
- Priority breakdown (CRITICAL, HIGH, MEDIUM, LOW)
- Category progress charts
- Status distribution
- Searchable/filterable document table with file paths
- Requirements tracking

**Data Source:** `data/contract_documents_complete_tracker.csv`

---

## Updating Dashboards

### Simple Method (Recommended)

1. Edit the CSV files in Excel/SharePoint:
   - `data/current_closeout.csv` - Update closeout requirement statuses
   - `data/contract_documents_complete_tracker.csv` - Update document review progress

2. Run the update command:
   ```bash
   update-montlake
   ```

3. View updated dashboards at GitHub Pages (updates in 1-2 minutes)

### Manual Method

If you prefer manual control:

```bash
# Generate dashboards
python3 scripts/closeout_dashboard_v3.py
python3 scripts/generate_review_dashboard.py

# Review locally
open index.html
open review-dashboard.html

# Commit and push
git add -A
git commit -m "Update dashboards"
git push
```

---

## Workflow

### Daily Document Review Workflow

1. **Open tracker in Excel:**
   ```bash
   open data/contract_documents_complete_tracker.csv
   ```

2. **Review documents and update:**
   - Set `Review_Status` to "In Progress" when starting
   - Document findings in `Closeout_Requirements_Found`
   - Add `Notes` as needed
   - Set `Review_Status` to "Reviewed" when complete
   - Fill in `Reviewer` and `Review_Date`

3. **Update dashboard:**
   ```bash
   update-montlake
   ```

See `docs/OPTIMAL_REVIEW_WORKFLOW.md` for detailed workflow guide.

---

## Utilities

### Scan Change Orders

Scan OneDrive for all change orders (001-189):

```bash
python3 scripts/utilities/scan_all_change_orders.py
```

Creates: `data/inventories/all_change_orders_inventory.csv`

### Scan Appendices

Scan OneDrive for all RFP appendices (1,063 files):

```bash
python3 scripts/utilities/scan_appendices.py
```

Creates: `data/inventories/appendices_inventory.csv`

### Generate Complete Document Tracker

Create fresh document tracker from OneDrive:

```bash
python3 scripts/utilities/create_final_complete_tracker.py
```

Creates: `data/contract_documents_complete_tracker.csv`

### View Review Progress

Show current review statistics:

```bash
python3 scripts/utilities/review_progress.py
```

### View Version History

Browse git version history:

```bash
scripts/utilities/view_versions.sh
```

---

## Data Files

### Active Data (Edit These)

- `data/current_closeout.csv` - Closeout requirements tracking
- `data/contract_documents_complete_tracker.csv` - Document review tracking

### Reference Data (Auto-Generated)

- `data/inventories/all_change_orders_inventory.csv` - All 189 change orders catalog
- `data/inventories/appendices_inventory.csv` - All 1,063 appendices catalog
- `data/inventories/appendices_summary.txt` - Appendices summary statistics

---

## Version Control

All changes are automatically tracked in Git:

```bash
# View history
git log --oneline

# View a specific version
git show <commit-hash>:data/current_closeout.csv

# Restore previous version
git checkout <commit-hash> data/current_closeout.csv
```

---

## Setup

The `update-montlake` command is an alias defined in `~/.zshrc`:

```bash
alias update-montlake='cd /Users/z/Desktop/git/montlake-closeout && ./update_dashboard.sh'
```

To use in a new terminal session:
```bash
source ~/.zshrc
```

---

## Technical Details

### Requirements

- Python 3 with pandas, plotly
- Git
- OneDrive sync (for document scanning utilities)

### GitHub Pages

Dashboards are automatically published via GitHub Pages:
- Repository: `zachjwd/montlake`
- Branch: `main`
- Source: Root directory
- Files: `index.html`, `review-dashboard.html`

Updates appear 1-2 minutes after pushing to GitHub.

---

## Documentation

See `docs/` directory for detailed guides:

- **OPTIMAL_REVIEW_WORKFLOW.md** - Step-by-step document review workflow
- **REVIEW_STATUS_PRESENTATION.md** - How to present review status to stakeholders
- **CONTRACT_DOCUMENTS_FOUND.md** - Complete catalog of all contract documents
- **APPENDIX_REVIEW_GUIDE.md** - Guide for reviewing appendices efficiently
- **DASHBOARD_USAGE.md** - Detailed dashboard feature documentation

---

**Project:** Montlake Bridge Replacement
**Purpose:** Track closeout requirements and document reviews
**Updated:** October 2025
