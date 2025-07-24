#!/bin/bash

# BlowControl HA Remote Branch Watcher
# This script helps keep your local main branch in sync with remote

set -e

echo "👀 BlowControl HA Remote Branch Watcher"
echo "======================================="

# Check if we're on main branch
current_branch=$(git rev-parse --abbrev-ref HEAD)
if [[ "$current_branch" != "main" ]]; then
    echo "⚠️  You're not on the main branch (currently on: $current_branch)"
    echo "   This script is designed to run from the main branch."
    echo "   Switch to main with: git checkout main"
    exit 1
fi

echo "📋 Current branch: $current_branch"
echo ""

# Fetch latest changes from remote
echo "📥 Fetching latest changes from remote..."
git fetch origin

# Check if remote main has new commits
remote_commits=$(git log --oneline main..origin/main | wc -l)
if [[ $remote_commits -gt 0 ]]; then
    echo "🔄 Remote main has $remote_commits new commit(s)"
    echo ""
    echo "Recent commits on remote main:"
    git log --oneline main..origin/main
    echo ""
    
    # Ask user if they want to pull
    read -p "Do you want to pull these changes? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📥 Pulling changes from remote main..."
        git pull origin main
        echo "✅ Successfully updated local main branch"
    else
        echo "❌ Skipped pulling changes"
    fi
else
    echo "✅ Local main branch is up to date with remote"
fi

echo ""
echo "🔍 Checking for any uncommitted changes..."
if [[ -n $(git status --porcelain) ]]; then
    echo "⚠️  You have uncommitted changes:"
    git status --short
    echo ""
    echo "💡 Consider committing or stashing these changes before switching branches"
else
    echo "✅ No uncommitted changes"
fi

echo ""
echo "📊 Branch status:"
echo "   Local main:  $(git rev-parse --short main)"
echo "   Remote main: $(git rev-parse --short origin/main)"
echo ""

# Check if there are any feature branches that might need rebasing
feature_branches=$(git branch --list "feature/*" --format="%(refname:short)")
if [[ -n "$feature_branches" ]]; then
    echo "🌿 Feature branches that might need rebasing:"
    echo "$feature_branches"
    echo ""
    echo "💡 Use './scripts/rebase-workflow.sh' on feature branches to rebase onto main"
fi
