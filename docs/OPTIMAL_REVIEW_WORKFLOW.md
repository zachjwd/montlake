# Optimal Document Review Workflow

## Overview

Simple, reliable workflow to track document reviews and keep HTML dashboard updated.

---

## 🎯 The Workflow (3 Steps)

### Step 1: Review Documents & Update Tracker

**Where:** Excel or SharePoint

**File:** `contract_documents_complete_tracker.csv`

**What to Update:**
- Review_Status: `Not Started` → `In Progress` → `Reviewed`
- Closeout_Requirements_Found: Brief summary
- Notes: Any observations
- Follow_Up_Required: `Yes` or `No`
- Reviewer: Your name
- Review_Date: `2025-01-18` format

**How Often:** As you review documents (daily/continuous)

---

### Step 2: Run One Command

```bash
update-review-dashboard
```

**What it does automatically:**
1. ✅ Reads your updated CSV tracker
2. ✅ Generates fresh HTML dashboard
3. ✅ Commits changes to Git (with timestamp)
4. ✅ Pushes to GitHub
5. ✅ Shows you a summary of progress

**How Often:** When you want to see updated dashboard (daily/weekly)

---

### Step 3: View Dashboard

**URL:** https://zachjwd.github.io/montlake/review-dashboard.html

**Auto-updates:** Within 1-2 minutes after Step 2

**Shows:**
- Overall progress
- Priority breakdown
- Category status
- Recent reviews
- Requirements found
- Missing/problem documents

---

## 📋 Detailed Workflow Steps

### Daily Work Process:

#### Morning:
```bash
# 1. Pull latest changes (if working with others)
cd /Users/z/Desktop/git/montlake-closeout
git pull

# 2. Open tracker
open contract_documents_complete_tracker.csv
```

#### During the Day:
- Review documents
- Update CSV as you go:
  - Mark status as "In Progress" when you start
  - Document findings in "Closeout_Requirements_Found"
  - Add notes
  - Mark "Reviewed" when complete
- Save CSV frequently (Excel auto-saves)

#### End of Day:
```bash
# 3. Update dashboard and backup
update-review-dashboard
```

Output shows:
```
📊 Document Review Dashboard Update
==================================

📋 Reading tracker...
✅ Loaded 1,261 documents

📊 Current Status:
   Reviewed:     125 documents (9.9%)
   In Progress:   45 documents (3.6%)
   Not Started: 1,091 documents (86.5%)

📈 Progress Today:
   +15 documents reviewed
   +8 closeout requirements found

🎨 Generating HTML dashboard...
✅ Dashboard created: review-dashboard.html

💾 Committing to Git...
   Changes: contract_documents_complete_tracker.csv, review-dashboard.html
   Commit: "Review progress: 15 docs reviewed (2025-01-18)"

🚀 Pushing to GitHub...
   Pushed to: https://github.com/zachjwd/montlake

✅ Done! Dashboard will be live in ~2 minutes
   View at: https://zachjwd.github.io/montlake/review-dashboard.html
```

---

## 🔄 Alternative Workflows

### Workflow A: SharePoint Editing (Team Collaboration)

**If multiple people reviewing:**

1. **Upload tracker to SharePoint:**
   - Put `contract_documents_complete_tracker.csv` in SharePoint
   - Multiple people can edit simultaneously

2. **Download before updating dashboard:**
   ```bash
   # Download CSV from SharePoint to local repo
   cp "/Users/z/OneDrive/.../contract_documents_complete_tracker.csv" \
      /Users/z/Desktop/git/montlake-closeout/

   # Generate dashboard
   update-review-dashboard
   ```

3. **Dashboard auto-publishes to GitHub Pages**

---

### Workflow B: Automatic Daily Updates (Advanced)

**Set up cron job to auto-update dashboard:**

```bash
# Edit crontab
crontab -e

# Add this line (updates at 5pm every weekday):
0 17 * * 1-5 cd /Users/z/Desktop/git/montlake-closeout && ./update-review-dashboard.sh

```

**Result:** Dashboard auto-updates every weekday at 5pm without you running command.

---

### Workflow C: Manual Control (No Auto-Commit)

**If you want to review before committing:**

```bash
# Generate dashboard only (no Git operations)
python3 generate_review_dashboard.py

# Review the dashboard locally
open review-dashboard.html

# If satisfied, manually commit
git add contract_documents_complete_tracker.csv review-dashboard.html
git commit -m "Review progress update"
git push
```

---

## 📊 What the HTML Dashboard Shows

### Page Layout:

```
┌─────────────────────────────────────────────────────────────┐
│                MONTLAKE DOCUMENT REVIEW DASHBOARD           │
│                  Last Updated: 2025-01-18 17:30             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  OVERALL PROGRESS                                           │
│  ┌───────────────────────────────────────┐                 │
│  │ [████████░░░░░░░░░░░░░░░░░] 9.9%      │                 │
│  │ 125 / 1,261 documents                 │                 │
│  └───────────────────────────────────────┘                 │
│                                                             │
│  KEY METRICS                                                │
│  ┌──────────┬──────────┬──────────┬──────────┐             │
│  │ Reviewed │In Progress│Not Started│   N/A   │             │
│  │   125    │    45     │  1,091    │    0    │             │
│  └──────────┴──────────┴──────────┴──────────┘             │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  PRIORITY STATUS                                            │
│  [Interactive Chart]                                        │
│  ┌─────────────────────────────────────────────┐           │
│  │ CRITICAL  [████████████████████] 53.6%      │           │
│  │ HIGH      [█████░░░░░░░░░░░░░░░] 14.2%      │           │
│  │ MEDIUM    [██░░░░░░░░░░░░░░░░░░]  5.4%      │           │
│  │ LOW       [█░░░░░░░░░░░░░░░░░░░]  3.3%      │           │
│  └─────────────────────────────────────────────┘           │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  CATEGORY BREAKDOWN                                         │
│  [Interactive Chart - Click to drill down]                 │
│  • Change Orders: 24/189 (12.7%)                            │
│  • Appendices: 100/1,063 (9.4%)                             │
│  • etc...                                                   │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  RECENT REVIEWS                                             │
│  ┌───────────────────────────────────────────────────┐     │
│  │ 2025-01-18 │ CO 189 Physical Completion Extension │     │
│  │ 2025-01-18 │ Appendix D1 - O&M Manual            │     │
│  │ 2025-01-17 │ CO 186 Multiple Issue Reso 11       │     │
│  └───────────────────────────────────────────────────┘     │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  CLOSEOUT REQUIREMENTS FOUND                                │
│  Total Requirements: 187                                    │
│  From 42 documents                                          │
│  [List with search/filter]                                  │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ISSUES & FOLLOW-UPS                                        │
│  ⚠️ CO 044: Completely missing                              │
│  ⚠️ 34 COs with folders but no executed PDFs                │
│  [Filterable list]                                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎨 Dashboard Features

### Interactive Elements:
- **Charts:** Click to drill down (e.g., click "Change Orders" to see individual COs)
- **Filters:** Filter by Priority, Status, Category
- **Search:** Search for specific documents
- **Sort:** Sort by any column
- **Export:** Download current view as CSV

### Auto-Calculations:
- Progress percentages
- Velocity (docs/day)
- Projected completion date
- Requirements summary

### Visual Indicators:
- ✅ Green = Complete
- 🔄 Yellow = In Progress
- ⏸️ Gray = Not Started
- ⚠️ Orange = Issues/Follow-up
- ❌ Red = Missing

---

## 🔐 Data Integrity & Backup

### Git Version Control:
Every time you run `update-review-dashboard`:
- CSV tracker is backed up to Git
- Full version history maintained
- Can rollback to any previous version

### View History:
```bash
# See all updates
git log --oneline contract_documents_complete_tracker.csv

# See what changed in a specific update
git show <commit-hash>

# Restore previous version if needed
git checkout <commit-hash> contract_documents_complete_tracker.csv
```

### Automatic Backups:
- Local: Git repository
- Cloud: GitHub (pushed automatically)
- OneDrive: If editing there, OneDrive versioning

---

## ⚙️ Configuration Options

### Update Frequency Settings:

Edit `~/.zshrc` to customize:

```bash
# Auto-commit on every update (default)
alias update-review-dashboard='cd /Users/z/Desktop/git/montlake-closeout && ./update_review_dashboard.sh'

# Manual commit (generate only, you commit later)
alias update-review-dashboard='cd /Users/z/Desktop/git/montlake-closeout && python3 generate_review_dashboard.py'

# Silent mode (no output, just update)
alias update-review-dashboard='cd /Users/z/Desktop/git/montlake-closeout && ./update_review_dashboard.sh --silent'
```

---

## 🚨 Error Handling

### If CSV is corrupted:
```bash
# Restore from Git
git checkout HEAD contract_documents_complete_tracker.csv

# Or restore from specific date
git checkout <commit-hash> contract_documents_complete_tracker.csv
```

### If dashboard won't generate:
```bash
# Check CSV for errors
python3 validate_tracker.py

# Shows any formatting issues, duplicate IDs, etc.
```

### If Git push fails:
```bash
# Pull latest changes first
git pull

# Resolve any conflicts in CSV
# Re-run update
update-review-dashboard
```

---

## 📈 Best Practices

### 1. Update Frequency:
- **Edit CSV:** Continuously as you review
- **Run dashboard update:** Daily or when presenting
- **Git commits:** Automatic with each dashboard update

### 2. Commit Messages:
Automatically generated based on your progress:
```
"Review progress: 15 docs reviewed, 8 requirements found (2025-01-18)"
```

### 3. Review Status Discipline:
- Set to "In Progress" when you START (prevents duplicates if multiple reviewers)
- Set to "Reviewed" only when COMPLETE
- Use "N/A" liberally for non-applicable docs

### 4. Notes Format:
Keep notes concise and consistent:
```
Good: "O&M manual required before PC; 1-yr warranty"
Bad: "This document talks about operations and maintenance..."
```

---

## 🔄 Integration with Existing Workflows

### Works with your existing `update-montlake` command:

```bash
# Update closeout documents dashboard
update-montlake

# Update document review dashboard
update-review-dashboard

# Both use same pattern:
# 1. Find/read CSV
# 2. Generate HTML
# 3. Commit to Git
# 4. Push to GitHub
```

---

## ✅ Summary: The Simple Daily Workflow

```bash
# Morning: Start work
open contract_documents_complete_tracker.csv

# During day: Review docs, update CSV
# (Just work in Excel, save as you go)

# End of day: Update dashboard
update-review-dashboard

# Done! Dashboard is live, Git is backed up
```

**That's it!** Three steps, one command, always current.

---

## 🎯 Next Steps

1. I'll create the HTML dashboard generator
2. I'll create the `update-review-dashboard` command
3. I'll test it end-to-end
4. You can start using it immediately

**Sound good?**
