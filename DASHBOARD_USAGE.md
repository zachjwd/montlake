# Montlake Dashboard Usage Guide

## Quick Start

### Update Dashboard (Simple!)

After downloading your CSV from SharePoint:

```bash
cd /Users/z/Desktop/git/montlake-closeout
./update_dashboard.sh
```

That's it! The script will:
1. 🔍 Find your CSV file (auto-detects in Desktop/Downloads)
2. 💾 Backup current version in Git
3. 🎨 Regenerate the dashboard
4. 🚀 Push to GitHub
5. ✅ Live in 1-2 minutes at https://zachjwd.github.io/montlake/

### Or Specify CSV Path Directly

```bash
./update_dashboard.sh "/Users/z/Desktop/git/Montlake - Closeout_101825.csv"
```

---

## Version History & Backups

All your CSV files are automatically backed up in Git! You can always go back to any previous version.

### View Version History

```bash
./view_versions.sh list
```

Shows recent updates:
```
abc1234 2025-01-17 Update dashboard from Montlake - Closeout_101725.csv
def5678 2025-01-10 Update dashboard from Montlake - Closeout_101025.csv
...
```

### See What Changed in a Version

```bash
./view_versions.sh show abc1234
```

### Restore a Previous Version

```bash
./view_versions.sh restore abc1234
```

Then run `./update_dashboard.sh` to regenerate dashboard with restored data.

### Compare Two Versions

```bash
./view_versions.sh compare abc1234 def5678
```

### Export a Previous Version to CSV

```bash
./view_versions.sh export abc1234 backup_jan17.csv
```

---

## How It Works

### File Structure

- `current_closeout.csv` - The "working" CSV (always updated with latest)
- `closeout_dashboard_v3.py` - Dashboard generator (reads from current_closeout.csv)
- `index.html` - Published dashboard (auto-generated)
- `update_dashboard.sh` - Main update script
- `view_versions.sh` - Version history tool

### CSV Naming

You can name your CSV files anything (e.g., "Montlake - Closeout_101725.csv", "closeout_final_v3.csv", etc.)

The script automatically:
- Finds your CSV
- Copies it to `current_closeout.csv`
- Stores the original name in the Git commit message
- All versions are preserved in Git history

### Version Control

Every update creates a Git commit with:
- Timestamp
- Original CSV filename
- Your custom message (optional)

Example commit history:
```
Update dashboard from Montlake - Closeout_101725.csv (2025-01-17 15:30)
Update dashboard from Montlake - Closeout_101025.csv (2025-01-10 14:15)
Update dashboard from closeout_v2.csv (2024-12-20 09:00)
```

---

## Common Workflows

### Daily Update
1. Edit Excel on SharePoint
2. Download CSV
3. Run `./update_dashboard.sh`

### Oh No, I Made a Mistake!
```bash
# See recent versions
./view_versions.sh list

# Restore previous version
./view_versions.sh restore abc1234

# Regenerate dashboard
./update_dashboard.sh
```

### Compare This Week's Changes
```bash
# List versions
./view_versions.sh list

# Compare two versions
./view_versions.sh compare abc1234 def5678
```

### Export for Reporting
```bash
# Export a specific version
./view_versions.sh export abc1234 report_jan17.csv
```

---

## Troubleshooting

### Script Can't Find CSV
- Make sure CSV is in Desktop or Downloads folder
- Or specify the full path: `./update_dashboard.sh /path/to/file.csv`

### Dashboard Generation Fails
- Check CSV format (must have headers: Req ID, Status, etc.)
- Make sure Python 3 is installed: `python3 --version`

### Git Push Fails
- Check internet connection
- Make sure you're authenticated with GitHub

### Need Help?
- Run scripts without arguments to see usage help
- Check Git history: `git log --oneline`

---

## Tips

💡 **Name your CSVs with dates** for easy tracking:
   - `Montlake - Closeout_101725.csv` (Jan 17, 2025)
   - `Montlake - Closeout_102025.csv` (Jan 20, 2025)

💡 **Review changes before pushing:**
   - Script shows Git status before committing
   - Add custom commit message when prompted

💡 **Keep Git history clean:**
   - Don't commit unrelated files
   - Use meaningful commit messages

💡 **Regular backups:**
   - Git is your backup! Every commit is a restore point
   - GitHub is your cloud backup

---

## Advanced: Manual Process

If you prefer to run steps manually:

```bash
cd /Users/z/Desktop/git/montlake-closeout

# 1. Copy your CSV
cp "/path/to/your/file.csv" current_closeout.csv

# 2. Generate dashboard
python3 closeout_dashboard_v3.py
cp /Users/z/Desktop/montlake_closeout.html index.html

# 3. Commit and push
git add current_closeout.csv index.html
git commit -m "Update dashboard"
git push
```
