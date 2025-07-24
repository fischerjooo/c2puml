#!/usr/bin/env python3
"""
Test Cleanup Script for C to PlantUML Converter

This script helps clean up redundant and overlapping test files that have been
consolidated into more organized test modules. It creates backups before deletion
and provides detailed reporting of the cleanup process.
"""

import os
import shutil
import time
from pathlib import Path
from typing import List, Set


def print_header(title: str, char: str = "=", width: int = 70):
    """Print a formatted header."""
    print(f"\n{char * width}")
    print(f"{title:^{width}}")
    print(f"{char * width}")


def print_info(message: str):
    """Print an info message."""
    print(f"ℹ️  {message}")


def print_success(message: str):
    """Print a success message."""
    print(f"✅ {message}")


def print_warning(message: str):
    """Print a warning message."""
    print(f"⚠️  {message}")


def print_error(message: str):
    """Print an error message."""
    print(f"❌ {message}")


def identify_redundant_tests() -> List[str]:
    """Identify test files that can be considered redundant based on analysis."""
    
    # These files have overlapping functionality that has been consolidated
    # into test_include_processing_consolidated.py
    redundant_files = [
        "tests/unit/test_include_processing.py",
        "tests/unit/test_include_processing_enhanced.py",
        "tests/unit/test_include_caching.py",
        "tests/unit/test_include_caching_integration.py",
    ]
    
    # Files that might be candidates for future consolidation
    potential_consolidation = [
        "tests/feature/test_include_processing_features.py",
        "tests/feature/test_include_processing_enhanced_features.py",
        "tests/feature/test_include_processing_integration.py",
        "tests/feature/test_include_dependency_processing.py",
    ]
    
    print_info("Redundant files identified:")
    for file_path in redundant_files:
        print(f"  - {file_path}")
    
    print_info("Files that could be consolidated in future:")
    for file_path in potential_consolidation:
        print(f"  - {file_path}")
    
    return redundant_files


def create_backup_directory() -> Path:
    """Create a timestamped backup directory."""
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    backup_dir = Path(f"test_backups_{timestamp}")
    backup_dir.mkdir(exist_ok=True)
    return backup_dir


def backup_file(file_path: str, backup_dir: Path) -> bool:
    """Backup a single file to the backup directory."""
    source_path = Path(file_path).resolve()
    if not source_path.exists():
        print_warning(f"File not found: {file_path}")
        return False

    # Preserve directory structure in backup
    try:
        relative_path = source_path.relative_to(Path.cwd().resolve())
    except ValueError:
        # If file is not in current directory tree, use just the filename
        relative_path = source_path.name
    backup_path = backup_dir / relative_path
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        shutil.copy2(source_path, backup_path)
        print_success(f"Backed up: {file_path} -> {backup_path}")
        return True
    except Exception as e:
        print_error(f"Failed to backup {file_path}: {e}")
        return False


def analyze_test_dependencies(file_path: str) -> Set[str]:
    """Analyze what functionality a test file covers (simplified analysis)."""
    dependencies = set()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().lower()
            
            # Simple keyword analysis
            if 'include' in content:
                dependencies.add('include_processing')
            if 'parse' in content:
                dependencies.add('parsing')
            if 'cache' in content or 'caching' in content:
                dependencies.add('caching')
            if 'typedef' in content:
                dependencies.add('typedef_processing')
            if 'relationship' in content:
                dependencies.add('relationships')
            if 'circular' in content:
                dependencies.add('circular_dependencies')
                
    except Exception as e:
        print_warning(f"Could not analyze {file_path}: {e}")
    
    return dependencies


def generate_cleanup_report(redundant_files: List[str], backup_dir: Path):
    """Generate a detailed cleanup report."""
    report_path = backup_dir / "cleanup_report.md"
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# Test Cleanup Report\n\n")
        f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## Summary\n\n")
        f.write("This report documents the cleanup of redundant test files in the ")
        f.write("C to PlantUML Converter test suite. The files listed below have been ")
        f.write("consolidated into more organized test modules to reduce duplication ")
        f.write("and improve maintainability.\n\n")
        
        f.write("## Redundant Files Removed\n\n")
        for file_path in redundant_files:
            if Path(file_path).exists():
                f.write(f"- `{file_path}`\n")
                
                # Analyze what this file was testing
                dependencies = analyze_test_dependencies(file_path)
                if dependencies:
                    f.write(f"  - Functionality: {', '.join(sorted(dependencies))}\n")
                
        f.write("\n## Consolidated Into\n\n")
        f.write("- `tests/unit/test_include_processing_consolidated.py`\n")
        f.write("- `tests/utils.py` (shared utilities)\n")
        f.write("- `tests/conftest.py` (pytest fixtures)\n\n")
        
        f.write("## Benefits\n\n")
        f.write("- Reduced code duplication\n")
        f.write("- Improved test organization\n")
        f.write("- Better test isolation\n")
        f.write("- Shared test utilities\n")
        f.write("- Consistent testing patterns\n\n")
        
        f.write("## Recovery\n\n")
        f.write("If any functionality was accidentally removed, the original files ")
        f.write(f"are backed up in this directory: `{backup_dir}`\n")
    
    print_success(f"Cleanup report generated: {report_path}")


def main():
    """Main cleanup function."""
    print_header("🧹 Test Suite Cleanup")
    
    print_info("This script will help clean up redundant test files.")
    print_info("All files will be backed up before removal.")
    
    # Identify redundant files
    redundant_files = identify_redundant_tests()
    
    if not redundant_files:
        print_success("No redundant files identified.")
        return
    
    # Confirm with user
    print(f"\nFound {len(redundant_files)} redundant files.")
    response = input("Do you want to proceed with cleanup? (y/N): ").lower().strip()
    
    if response not in ['y', 'yes']:
        print_info("Cleanup cancelled by user.")
        return
    
    # Create backup directory
    backup_dir = create_backup_directory()
    print_success(f"Created backup directory: {backup_dir}")
    
    # Backup files
    print_header("📦 Backing Up Files")
    backup_success = []
    
    for file_path in redundant_files:
        if backup_file(file_path, backup_dir):
            backup_success.append(file_path)
    
    if len(backup_success) != len(redundant_files):
        print_error("Some files could not be backed up. Aborting cleanup.")
        return
    
    # Remove redundant files
    print_header("🗑️  Removing Redundant Files")
    removed_files = []
    
    for file_path in redundant_files:
        try:
            os.remove(file_path)
            print_success(f"Removed: {file_path}")
            removed_files.append(file_path)
        except Exception as e:
            print_error(f"Failed to remove {file_path}: {e}")
    
    # Generate report
    print_header("📊 Generating Report")
    generate_cleanup_report(removed_files, backup_dir)
    
    # Final summary
    print_header("✨ Cleanup Complete")
    print(f"Files backed up: {len(backup_success)}")
    print(f"Files removed: {len(removed_files)}")
    print(f"Backup location: {backup_dir}")
    
    if removed_files:
        print_success("Test suite cleanup completed successfully!")
        print_info("Run tests to verify everything still works:")
        print_info("  python run_all_tests.py --stats")
    else:
        print_warning("No files were removed.")


if __name__ == "__main__":
    main()