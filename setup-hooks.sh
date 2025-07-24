#!/bin/bash
# Setup script to install git hooks on Linux

echo "Setting up git hooks..."

# Remove existing pre-commit hook if it exists
if [ -f ".git/hooks/pre-commit" ]; then
    echo "Removing existing pre-commit hook..."
    rm .git/hooks/pre-commit
fi

echo "Installing pre-commit hook..."
cp hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

echo "✅ Git hooks setup complete!"
echo "The pre-commit hook will now run Black and isort checks before each commit."