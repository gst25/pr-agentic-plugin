#!/bin/bash
# Automatically format, commit, and push plugin changes to GitHub

echo "🎨 Formatting code..."
python3 -m black .
python3 -m isort .

echo "📝 Staging changes..."
git add .

# Default commit message if none provided
COMMIT_MSG=${1:-"chore: auto-push updates"}

echo "💾 Committing changes with message: '$COMMIT_MSG'..."
git commit -m "$COMMIT_MSG"

echo "🚀 Pushing to GitHub..."
git push

echo "✅ All done!"
