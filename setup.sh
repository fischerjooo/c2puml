#!/bin/bash
set -e

echo "Setting up c2puml development environment..."

# Check if python3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed or not in PATH"
    exit 1
fi

echo "Python3 version: $(python3 --version)"

# Install the package in development mode
echo "Installing c2puml in development mode..."
python3 -m pip install -e . --break-system-packages

# Add the local bin directory to PATH for this session
export PATH="/home/ubuntu/.local/bin:$PATH"

echo "Installation complete!"
echo ""
echo "To run the example:"
echo "  ./run_example.sh"
echo ""
echo "Or manually:"
echo "  export PATH=\"/home/ubuntu/.local/bin:\$PATH\""
echo "  export PYTHONPATH=src"
echo "  python3 -m c2puml.main --config tests/example/config.json --verbose"
echo ""
echo "Note: You may need to add the PATH export to your shell profile for permanent access."