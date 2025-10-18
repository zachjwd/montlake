#!/bin/bash

# Montlake Dashboard Update Script
# Usage: ./update_dashboard.sh [path-to-csv]
# If no path provided, will search Desktop and Downloads for CSV files

set -e

REPO_DIR="/Users/z/Desktop/git/montlake-closeout"
DESKTOP_DIR="/Users/z/Desktop/git"
DOWNLOADS_DIR="/Users/z/Downloads"
CSV_NAME="current_closeout.csv"

cd "$REPO_DIR"

echo "🔍 Montlake Dashboard Update Tool"
echo "=================================="
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
    mapfile -t CSV_FILES < <(find_csv_files)

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
echo "📁 Using file: $(basename "$CSV_FILE")"
ORIGINAL_NAME=$(basename "$CSV_FILE")

# Copy new CSV to repo with standard name (if not already there)
if [ "$(realpath "$CSV_FILE")" = "$REPO_DIR/$CSV_NAME" ]; then
    echo "📋 Using existing $CSV_NAME in repository..."
else
    # Backup old CSV if it exists (Git will track this)
    if [ -f "$REPO_DIR/$CSV_NAME" ]; then
        echo "💾 Current CSV will be backed up in Git history"
    fi
    echo "📋 Copying CSV to repository..."
    cp "$CSV_FILE" "$REPO_DIR/$CSV_NAME"
fi

# Update Python script to use standard CSV name if needed
if ! grep -q "current_closeout.csv" closeout_dashboard_v3.py; then
    echo "🔧 Updating Python script to use standard CSV name..."
    sed -i '' "s/pd.read_csv('[^']*\.csv'/pd.read_csv('$CSV_NAME'/g" closeout_dashboard_v3.py
fi

# Generate dashboard
echo "🎨 Generating dashboard..."
python3 closeout_dashboard_v3.py

if [ $? -ne 0 ]; then
    echo "❌ Error generating dashboard"
    exit 1
fi

# Copy to index.html
echo "📄 Updating index.html..."
cp /Users/z/Desktop/montlake_closeout.html index.html

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
git add $CSV_NAME closeout_dashboard_v3.py index.html

# Check if there are changes to commit
if git diff --staged --quiet; then
    echo "ℹ️  No changes to commit (data unchanged)"
else
    git commit -m "$COMMIT_MSG"

    # Push to GitHub
    echo "🚀 Pushing to GitHub..."
    git push

    echo ""
    echo "✅ Dashboard updated successfully!"
    echo ""
    echo "📈 Dashboard will be live at: https://zachjwd.github.io/montlake/"
    echo "⏱️  GitHub Pages usually updates within 1-2 minutes"
fi

echo ""
echo "💡 Version tracking:"
echo "   - All CSV versions are saved in Git history"
echo "   - To see history: git log --oneline"
echo "   - To see a previous CSV: git show <commit-hash>:$CSV_NAME"
echo "   - To revert to previous version: git revert <commit-hash>"
echo ""
