#!/usr/bin/env python3
"""
Demonstration of the crypto filter pattern issue

This script demonstrates why the filter pattern:
"include": ["^crypto.*//.c$", "^crypto.*//.h$"]

does not work and shows the correct solutions.
"""

import re
import tempfile
from pathlib import Path
from c_to_plantuml.config import Config


def create_test_files(temp_dir):
    """Create test files for demonstration"""
    crypto_files = [
        "Crypto_Cfg_Partitions.c",
        "Crypto_Cfg_JobQueues.c", 
        "Crypto.c",
        "Crypto.h",
        "Crypto_Cfg_Partitions.h",
        "Crypto_Cfg_JobQueues.h"
    ]
    
    other_files = [
        "main.c",
        "utils.c",
        "config.h",
        "types.h"
    ]
    
    for filename in crypto_files + other_files:
        file_path = temp_dir / filename
        with open(file_path, 'w') as f:
            f.write(f"// Test file: {filename}\n")
            f.write("#include <stdio.h>\n")
            f.write("// End of file\n")


def test_pattern(pattern, filename):
    """Test if a pattern matches a filename"""
    try:
        return bool(re.search(pattern, filename))
    except re.error as e:
        return f"INVALID PATTERN: {e}"


def demonstrate_issue():
    """Demonstrate the crypto filter pattern issue"""
    print("🔍 CRYPTO FILTER PATTERN ISSUE DEMONSTRATION")
    print("=" * 60)
    
    # Create temporary test files
    temp_dir = Path(tempfile.mkdtemp())
    create_test_files(temp_dir)
    
    test_files = [
        "Crypto_Cfg_Partitions.c",
        "Crypto_Cfg_JobQueues.c", 
        "Crypto.c",
        "Crypto.h",
        "Crypto_Cfg_Partitions.h",
        "Crypto_Cfg_JobQueues.h"
    ]
    
    print("\n📁 Test files created:")
    for filename in test_files:
        print(f"   - {filename}")
    
    print("\n❌ PROBLEMATIC PATTERN (from user's question):")
    print('   "include": ["^crypto.*//.c$", "^crypto.*//.h$"]')
    print("\n   This pattern is BROKEN because:")
    print("   1. '//' is interpreted as literal forward slashes")
    print("   2. It's case-sensitive (looks for 'crypto', not 'Crypto')")
    print("   3. The pattern expects 'crypto' followed by '//' followed by '.c'")
    
    broken_patterns = ["^crypto.*//.c$", "^crypto.*//.h$"]
    
    print("\n   Test results:")
    for filename in test_files:
        for pattern in broken_patterns:
            result = test_pattern(pattern, filename)
            print(f"     {pattern} -> {filename}: {result}")
    
    print("\n✅ CORRECTED PATTERNS:")
    
    # Pattern 1: Case-insensitive with proper escaping
    print("\n   1. Case-insensitive with proper escaping:")
    print('   "include": ["(?i)^crypto.*\\.c$", "(?i)^crypto.*\\.h$"]')
    
    fixed_patterns = ["(?i)^crypto.*\\.c$", "(?i)^crypto.*\\.h$"]
    
    print("\n   Test results:")
    for filename in test_files:
        for pattern in fixed_patterns:
            result = test_pattern(pattern, filename)
            print(f"     {pattern} -> {filename}: {result}")
    
    # Pattern 2: Alternative approaches
    print("\n   2. Alternative pattern approaches:")
    
    alternatives = [
        ("Word boundary with case-insensitive", ["(?i)\\bcrypto.*\\.c$", "(?i)\\bcrypto.*\\.h$"]),
        ("Any file containing crypto", [".*crypto.*\\.c$", ".*crypto.*\\.h$"]),
        ("Specific crypto config files", ["(?i)^crypto.*cfg.*\\.c$", "(?i)^crypto.*cfg.*\\.h$"])
    ]
    
    for desc, patterns in alternatives:
        print(f"\n   {desc}:")
        print(f"   {patterns}")
        print("   Test results:")
        for filename in test_files:
            for pattern in patterns:
                result = test_pattern(pattern, filename)
                print(f"     {pattern} -> {filename}: {result}")
    
    print("\n🔧 RECOMMENDED SOLUTION:")
    print("   Use case-insensitive patterns with proper regex escaping:")
    print('   "include": ["(?i)^crypto.*\\.c$", "(?i)^crypto.*\\.h$"]')
    print("\n   This pattern:")
    print("   - (?i) makes it case-insensitive")
    print("   - ^crypto matches files starting with 'crypto' (any case)")
    print("   - .* matches any characters")
    print("   - \\.c$ matches literal '.c' at the end")
    
    # Test with Config class
    print("\n🧪 TESTING WITH CONFIG CLASS:")
    
    config = Config(
        source_folders=[str(temp_dir)],
        file_filters={
            "include": ["(?i)^crypto.*\\.c$", "(?i)^crypto.*\\.h$"]
        }
    )
    
    print("   Testing file inclusion:")
    for filename in test_files:
        should_include = config._should_include_file(filename)
        print(f"     {filename}: {should_include}")
    
    # Clean up
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)
    
    print("\n" + "=" * 60)
    print("✅ DEMONSTRATION COMPLETE")
    print("\n📝 SUMMARY:")
    print("   The original pattern '^crypto.*//.c$' doesn't work because:")
    print("   1. '//' is literal, not a path separator")
    print("   2. It's case-sensitive")
    print("   3. The regex syntax is incorrect")
    print("\n   The correct pattern is '(?i)^crypto.*\\.c$' which:")
    print("   1. Uses (?i) for case-insensitive matching")
    print("   2. Uses \\. to escape the literal dot")
    print("   3. Uses $ to match end of string")


def show_regex_explanation():
    """Show detailed regex explanation"""
    print("\n📚 REGEX PATTERN EXPLANATION")
    print("=" * 40)
    
    patterns = [
        ("^crypto.*//.c$", "Broken pattern from user's question"),
        ("(?i)^crypto.*\\.c$", "Corrected pattern"),
        ("(?i)\\bcrypto.*\\.c$", "With word boundary"),
        (".*crypto.*\\.c$", "Any file containing crypto")
    ]
    
    for pattern, description in patterns:
        print(f"\n{description}:")
        print(f"  Pattern: {pattern}")
        print("  Breakdown:")
        
        if pattern == "^crypto.*//.c$":
            print("    ^ - Start of string")
            print("    crypto - Literal 'crypto' (case-sensitive)")
            print("    .* - Any characters")
            print("    // - Literal forward slashes (WRONG!)")
            print("    .c - Literal '.c'")
            print("    $ - End of string")
            print("    ❌ This will never match 'Crypto.c'")
            
        elif pattern == "(?i)^crypto.*\\.c$":
            print("    (?i) - Case-insensitive flag")
            print("    ^ - Start of string")
            print("    crypto - Literal 'crypto' (case-insensitive)")
            print("    .* - Any characters")
            print("    \\. - Escaped literal dot")
            print("    c - Literal 'c'")
            print("    $ - End of string")
            print("    ✅ This will match 'Crypto.c', 'crypto.c', etc.")
            
        elif pattern == "(?i)\\bcrypto.*\\.c$":
            print("    (?i) - Case-insensitive flag")
            print("    \\b - Word boundary")
            print("    crypto - Literal 'crypto' (case-insensitive)")
            print("    .* - Any characters")
            print("    \\. - Escaped literal dot")
            print("    c - Literal 'c'")
            print("    $ - End of string")
            print("    ✅ This will match 'Crypto.c' but not 'mycrypto.c'")
            
        elif pattern == ".*crypto.*\\.c$":
            print("    .* - Any characters")
            print("    crypto - Literal 'crypto' (case-sensitive)")
            print("    .* - Any characters")
            print("    \\. - Escaped literal dot")
            print("    c - Literal 'c'")
            print("    $ - End of string")
            print("    ⚠️ This will match 'mycrypto.c' but not 'Crypto.c'")


if __name__ == "__main__":
    demonstrate_issue()
    show_regex_explanation()