#!/bin/bash

# Montlake All Dashboards Update Script
# Updates both closeout dashboard and requirements dashboard
# Usage: ./update_dashboard.sh [path-to-closeout-csv]
# If no path provided, will search Desktop and Downloads for CSV files

set -e

REPO_DIR="/Users/z/Desktop/git/montlake-closeout"
DESKTOP_DIR="/Users/z/Desktop/git"
DOWNLOADS_DIR="/Users/z/Downloads"
CLOSEOUT_CSV="data/current_closeout.csv"
REVIEW_CSV="data/contract_documents_complete_tracker.csv"

cd "$REPO_DIR"

echo "🔍 Montlake All Dashboards Update Tool"
echo "========================================"
echo ""

# Function to find CSV files
find_csv_files() {
    find "$DESKTOP_DIR" "$DOWNLOADS_DIR" -maxdepth 1 -name "*.csv" -type f 2>/dev/null | grep -i "montlake\|closeout" | sort
}

# If CSV path provided as argument, use it
if [ -n "$1" ]; then
    CSV_FILE="$1"
    if [ ! -f "$CSV_FILE" ]; then
        echo "❌ Error: File not found: $CSV_FILE"
        exit 1
    fi
else
    # Search for CSV files
    echo "🔍 Searching for Montlake/Closeout CSV files..."

    # Read files into array properly handling spaces
    CSV_FILES=()
    while IFS= read -r file; do
        CSV_FILES+=("$file")
    done < <(find_csv_files)

    if [ ${#CSV_FILES[@]} -eq 0 ]; then
        echo "❌ No Montlake/Closeout CSV files found in Desktop or Downloads"
        echo ""
        echo "Usage: ./update_dashboard.sh /path/to/your/file.csv"
        exit 1
    elif [ ${#CSV_FILES[@]} -eq 1 ]; then
        CSV_FILE="${CSV_FILES[0]}"
        echo "✅ Found: $(basename "$CSV_FILE")"
    else
        echo "📋 Multiple CSV files found:"
        echo ""
        for i in "${!CSV_FILES[@]}"; do
            echo "  $((i+1)). $(basename "${CSV_FILES[$i]}")"
        done
        echo ""
        read -p "Select file (1-${#CSV_FILES[@]}): " selection

        if ! [[ "$selection" =~ ^[0-9]+$ ]] || [ "$selection" -lt 1 ] || [ "$selection" -gt ${#CSV_FILES[@]} ]; then
            echo "❌ Invalid selection"
            exit 1
        fi

        CSV_FILE="${CSV_FILES[$((selection-1))]}"
    fi
fi

echo ""
echo "📁 Using closeout CSV: $(basename "$CSV_FILE")"
ORIGINAL_NAME=$(basename "$CSV_FILE")

# Copy new closeout CSV to repo with standard name (if not already there)
if [ "$(realpath "$CSV_FILE")" = "$REPO_DIR/$CLOSEOUT_CSV" ]; then
    echo "📋 Using existing $CLOSEOUT_CSV in repository..."
else
    # Backup old CSV if it exists (Git will track this)
    if [ -f "$REPO_DIR/$CLOSEOUT_CSV" ]; then
        echo "💾 Current CSV will be backed up in Git history"
    fi
    echo "📋 Copying closeout CSV to repository..."
    cp "$CSV_FILE" "$REPO_DIR/$CLOSEOUT_CSV"
fi

# Update Python script to use standard CSV name if needed
if ! grep -q "data/current_closeout.csv" scripts/closeout_dashboard_v3.py; then
    echo "🔧 Updating Python script to use standard CSV name..."
    sed -i '' "s|pd.read_csv('[^']*current_closeout\.csv'|pd.read_csv('$CLOSEOUT_CSV'|g" scripts/closeout_dashboard_v3.py
fi

echo ""
echo "🎨 Generating dashboards..."
echo ""

# Generate closeout requirements dashboard
echo "1️⃣  Generating closeout requirements dashboard..."
python3 scripts/closeout_dashboard_v3.py

if [ $? -ne 0 ]; then
    echo "❌ Error generating closeout dashboard"
    exit 1
fi

# Copy to dashboard directory
echo "   ✅ Closeout dashboard created"
cp /Users/z/Desktop/montlake_closeout.html dashboard/closeout_dashboard.html

# Generate requirements dashboard
echo "2️⃣  Generating requirements dashboard..."
python3 scripts/generate_requirements_dashboard.py

if [ $? -ne 0 ]; then
    echo "❌ Error generating requirements dashboard"
    exit 1
fi

echo "   ✅ Requirements dashboard created"

# Show changes
echo ""
echo "📊 Git Status:"
git status --short

echo ""
read -p "💬 Commit message (or press Enter for default): " COMMIT_MSG

if [ -z "$COMMIT_MSG" ]; then
    COMMIT_MSG="Update dashboard from $ORIGINAL_NAME ($(date '+%Y-%m-%d %H:%M'))"
fi

# Commit changes
echo "💾 Committing changes..."
git add $CLOSEOUT_CSV $REVIEW_CSV scripts/closeout_dashboard_v3.py scripts/generate_requirements_dashboard.py dashboard/closeout_dashboard.html dashboard/requirements_dashboard.html data/review_tracker.csv data/requirements_tracker.csv

# Check if there are changes to commit
if git diff --staged --quiet; then
    echo "ℹ️  No changes to commit (data unchanged)"
else
    git commit -m "$COMMIT_MSG"

    # Push to GitHub
    echo "🚀 Pushing to GitHub..."
    git push

    echo ""
    echo "✅ All dashboards updated successfully!"
    echo ""
    echo "📈 Dashboards available at:"
    echo "   Closeout Dashboard:     dashboard/closeout_dashboard.html"
    echo "   Requirements Dashboard: dashboard/requirements_dashboard.html"
    echo ""
    echo "   (If GitHub Pages is enabled, they will be live shortly)"
fi

echo ""
echo "💡 Version tracking:"
echo "   - All CSV versions are saved in Git history"
echo "   - To see history: git log --oneline"
echo "   - To see a previous CSV: git show <commit-hash>:$CLOSEOUT_CSV"
echo "   - To revert to previous version: git revert <commit-hash>"
echo ""
