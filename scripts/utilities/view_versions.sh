#!/bin/bash

# Version History Helper Script
# View and restore previous CSV versions

set -e

REPO_DIR="/Users/z/Desktop/git/montlake-closeout"
CSV_NAME="current_closeout.csv"

cd "$REPO_DIR"

echo "📜 Montlake Dashboard Version History"
echo "======================================"
echo ""

# Function to show CSV history
show_history() {
    echo "Recent CSV updates:"
    echo ""
    git log --oneline --follow --date=short --format="%h %ad %s" -- "$CSV_NAME" | head -20
    echo ""
}

# Function to show what changed in a commit
show_changes() {
    local commit=$1
    echo "📊 Changes in commit $commit:"
    echo ""

    # Get commit info
    git log -1 --format="%h - %s (%ad)" --date=short $commit
    echo ""

    # Try to show CSV stats comparison
    echo "File size comparison:"
    PREV_SIZE=$(git show $commit^:$CSV_NAME 2>/dev/null | wc -c)
    CURR_SIZE=$(git show $commit:$CSV_NAME | wc -c)
    echo "  Before: $PREV_SIZE bytes"
    echo "  After:  $CURR_SIZE bytes"
    echo ""
}

# Function to restore a version
restore_version() {
    local commit=$1

    echo "⚠️  This will restore $CSV_NAME from commit $commit"
    echo ""
    git log -1 --format="%h - %s (%ad)" --date=short $commit
    echo ""
    read -p "Continue? (yes/no): " confirm

    if [ "$confirm" != "yes" ]; then
        echo "❌ Cancelled"
        exit 0
    fi

    # Restore the file
    git checkout $commit -- $CSV_NAME

    echo "✅ Restored $CSV_NAME from commit $commit"
    echo ""
    echo "Next steps:"
    echo "  1. Review the restored CSV"
    echo "  2. Run ./update_dashboard.sh to regenerate dashboard"
    echo "  3. Or run 'git restore $CSV_NAME' to undo this restoration"
}

# Function to compare two versions
compare_versions() {
    local commit1=$1
    local commit2=$2

    echo "📊 Comparing CSV versions:"
    echo ""
    git log -1 --format="Version 1: %h - %s (%ad)" --date=short $commit1
    git log -1 --format="Version 2: %h - %s (%ad)" --date=short $commit2
    echo ""

    # Show line count difference
    LINES1=$(git show $commit1:$CSV_NAME | wc -l)
    LINES2=$(git show $commit2:$CSV_NAME | wc -l)
    DIFF=$((LINES2 - LINES1))

    echo "Line counts:"
    echo "  Version 1: $LINES1 lines"
    echo "  Version 2: $LINES2 lines"
    if [ $DIFF -gt 0 ]; then
        echo "  Change: +$DIFF lines added"
    elif [ $DIFF -lt 0 ]; then
        echo "  Change: $DIFF lines removed"
    else
        echo "  Change: No line count difference"
    fi
    echo ""
}

# Main menu
if [ "$1" = "list" ] || [ -z "$1" ]; then
    show_history

elif [ "$1" = "show" ]; then
    if [ -z "$2" ]; then
        echo "Usage: ./view_versions.sh show <commit-hash>"
        exit 1
    fi
    show_changes "$2"

elif [ "$1" = "restore" ]; then
    if [ -z "$2" ]; then
        echo "Usage: ./view_versions.sh restore <commit-hash>"
        echo ""
        show_history
        exit 1
    fi
    restore_version "$2"

elif [ "$1" = "compare" ]; then
    if [ -z "$2" ] || [ -z "$3" ]; then
        echo "Usage: ./view_versions.sh compare <commit-hash-1> <commit-hash-2>"
        exit 1
    fi
    compare_versions "$2" "$3"

elif [ "$1" = "export" ]; then
    if [ -z "$2" ]; then
        echo "Usage: ./view_versions.sh export <commit-hash> [output-file.csv]"
        exit 1
    fi

    OUTPUT="${3:-exported_${2}.csv}"
    git show $2:$CSV_NAME > "$OUTPUT"
    echo "✅ Exported CSV from commit $2 to: $OUTPUT"

else
    echo "Montlake Dashboard Version History Tool"
    echo ""
    echo "Usage:"
    echo "  ./view_versions.sh list              - Show recent CSV versions"
    echo "  ./view_versions.sh show <commit>     - Show what changed in a commit"
    echo "  ./view_versions.sh restore <commit>  - Restore CSV from a previous commit"
    echo "  ./view_versions.sh compare <c1> <c2> - Compare two versions"
    echo "  ./view_versions.sh export <commit> [file] - Export CSV from a commit"
    echo ""
    echo "Examples:"
    echo "  ./view_versions.sh list"
    echo "  ./view_versions.sh show abc1234"
    echo "  ./view_versions.sh restore abc1234"
    echo "  ./view_versions.sh compare abc1234 def5678"
    echo "  ./view_versions.sh export abc1234 backup.csv"
    echo ""
fi
