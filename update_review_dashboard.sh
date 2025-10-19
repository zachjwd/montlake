#!/bin/bash

# Update Review Dashboard Script
# Generates HTML dashboard from contract_documents_complete_tracker.csv
# Auto-commits and pushes to GitHub

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "📊 Document Review Dashboard Update"
echo "=================================="
echo ""

# Check if tracker CSV exists
TRACKER_CSV="contract_documents_complete_tracker.csv"
if [ ! -f "$TRACKER_CSV" ]; then
    echo "❌ Error: $TRACKER_CSV not found"
    echo "   Make sure you're in the montlake-closeout directory"
    exit 1
fi

# Generate dashboard
echo "📋 Reading tracker..."
python3 generate_review_dashboard.py

if [ ! -f "review-dashboard.html" ]; then
    echo "❌ Error: Dashboard generation failed"
    exit 1
fi

echo ""

# Git operations
echo "💾 Committing to Git..."

# Get current stats for commit message
REVIEWED=$(python3 -c "import pandas as pd; df=pd.read_csv('$TRACKER_CSV', encoding='utf-8-sig'); print(len(df[df['Review_Status']=='Reviewed']))")
TOTAL=$(python3 -c "import pandas as pd; df=pd.read_csv('$TRACKER_CSV', encoding='utf-8-sig'); print(len(df))")
REQS=$(python3 -c "import pandas as pd; df=pd.read_csv('$TRACKER_CSV', encoding='utf-8-sig'); print(len(df[df['Closeout_Requirements_Found']!='']))")

DATE=$(date +"%Y-%m-%d")
COMMIT_MSG="Review progress: $REVIEWED/$TOTAL docs reviewed, $REQS requirements found ($DATE)"

# Check if there are changes
if git diff --quiet HEAD -- "$TRACKER_CSV" "review-dashboard.html" 2>/dev/null; then
    echo "   No changes to commit"
else
    git add "$TRACKER_CSV" review-dashboard.html
    git commit -m "$COMMIT_MSG" || true

    echo ""
    echo "🚀 Pushing to GitHub..."
    git push

    echo ""
    echo "✅ Done! Dashboard will be live in ~2 minutes"
    echo "   View at: https://zachjwd.github.io/montlake/review-dashboard.html"
fi

echo ""
echo "📊 Current Status:"
echo "   Reviewed:     $REVIEWED/$TOTAL documents"
echo "   Requirements: $REQS found"
echo ""
