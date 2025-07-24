#!/bin/bash

# Setup script to install git hooks

echo "Setting up git hooks..."

# Create symbolic link for pre-commit hook
if [ -f ".git/hooks/pre-commit" ]; then
    echo "Removing existing pre-commit hook..."
    rm .git/hooks/pre-commit
fi

echo "Installing pre-commit hook..."
ln -sf ../../hooks/pre-commit .git/hooks/pre-commit

echo "✅ Git hooks setup complete!"
echo "The pre-commit hook will now run Black and isort checks before each commit."