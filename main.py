#!/usr/bin/env python3
"""
Minimal standalone wrapper for c2puml
"""

import sys
from pathlib import Path

# Add the src directory to Python path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
if src_dir.exists():
    sys.path.insert(0, str(src_dir))
else:
    print("Error: src directory not found. Make sure this script is in the root directory of the c2puml project.")
    sys.exit(1)

# Import and run the main function
from c2puml.main import main
sys.exit(main())