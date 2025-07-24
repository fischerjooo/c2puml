#!/bin/bash
# Comprehensive Linux setup script for C to PlantUML Converter

set -e  # Exit on any error

echo "🚀 Setting up C to PlantUML Converter development environment on Linux"
echo "=" * 60

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "❌ Please don't run this script as root. Run as a regular user."
    exit 1
fi

# Update system packages
echo "📦 Updating system packages..."
sudo apt update

# Install required system packages
echo "📦 Installing required system packages..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3.13-venv \
    python3.13-dev \
    git \
    build-essential

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists. Removing..."
    rm -rf venv
fi

python3 -m venv venv

# Activate virtual environment and install dependencies
echo "📦 Installing Python dependencies..."
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install development dependencies
echo "📦 Installing development dependencies..."
pip install -r requirements-dev.txt

# Install the package in development mode
echo "📦 Installing package in development mode..."
pip install -e .

# Set up git hooks
echo "🔧 Setting up git hooks..."
./setup-hooks.sh

# Test the setup
echo "🧪 Testing the setup..."
echo "Testing Black formatter..."
black --version

echo "Testing isort..."
isort --version

echo "Testing flake8..."
flake8 --version

echo "Testing pre-commit hook..."
.git/hooks/pre-commit

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Open VSCode in this directory"
echo "3. VSCode should automatically detect the Python interpreter in ./venv/bin/python"
echo "4. Python auto-formatting should now work when you save files"
echo "5. Pre-commit hooks will run automatically on git commit"
echo ""
echo "🔧 Manual VSCode configuration (if needed):"
echo "- Press Ctrl+Shift+P and run 'Python: Select Interpreter'"
echo "- Choose './venv/bin/python' from the list"
echo "- Ensure the Python extension is installed"
echo ""
echo "🎉 Happy coding!"