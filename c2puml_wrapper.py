#!/usr/bin/env python3
"""
c2puml Wrapper Script - No Installation Required

This script automatically sets up the Python path and runs c2puml
without requiring any installation. Just run:

    python c2puml_wrapper.py --config tests/example/config.json --verbose
"""

import os
import sys
from pathlib import Path

def setup_path():
    """Automatically add src directory to Python path."""
    # Get the directory where this script is located
    script_dir = Path(__file__).resolve().parent
    
    # Look for the src directory
    src_path = script_dir / "src"
    if src_path.exists():
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))
            print(f"🔧 Auto-added {src_path} to Python path")
        return True
    
    # If not found, look for src in parent directories
    for parent in script_dir.parents:
        src_path = parent / "src"
        if src_path.exists():
            if str(src_path) not in sys.path:
                sys.path.insert(0, str(src_path))
                print(f"🔧 Auto-added {src_path} to Python path")
            return True
    
    return False

def main():
    """Main function that sets up path and runs c2puml."""
    # Set up the path
    if not setup_path():
        print("❌ Error: Could not find src directory")
        print("Make sure you're running this from the project root directory")
        return 1
    
    # Import and run c2puml
    try:
        from c2puml.main import main as c2puml_main
        return c2puml_main()
    except ImportError as e:
        print(f"❌ Error importing c2puml: {e}")
        print("Make sure you're in the correct directory with the src folder")
        return 1
    except Exception as e:
        print(f"❌ Error running c2puml: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())