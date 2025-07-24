#!/bin/bash

# BlowControl HA Rebase Workflow Script
# This script helps maintain a clean rebase workflow

set -e

echo "🔄 BlowControl HA Rebase Workflow"
echo "=================================="

# Check if we're on a feature branch
current_branch=$(git branch --show-current)

if [[ "$current_branch" == "main" ]]; then
    echo "❌ Error: You're on the main branch. Please switch to a feature branch first."
    exit 1
fi

echo "📋 Current branch: $current_branch"
echo ""

# Fetch latest changes from remote
echo "📥 Fetching latest changes from remote..."
git fetch origin

# Check if main has new commits
main_commits=$(git log --oneline main..origin/main | wc -l)
if [[ $main_commits -gt 0 ]]; then
    echo "⚠️  Main branch has $main_commits new commit(s)"
    echo "📥 Updating main branch..."
    git checkout main
    git pull origin main
    git checkout "$current_branch"
else
    echo "✅ Main branch is up to date"
fi

# Perform rebase
echo ""
echo "🔄 Rebasing $current_branch onto main..."
if git rebase main; then
    echo "✅ Rebase successful!"
    echo ""
    echo "📤 You can now push your changes:"
    echo "   git push origin $current_branch --force-with-lease"
else
    echo "❌ Rebase failed. Please resolve conflicts and continue with:"
    echo "   git rebase --continue"
    echo "   or"
    echo "   git rebase --abort"
    exit 1
fi
