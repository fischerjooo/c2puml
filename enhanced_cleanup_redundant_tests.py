#!/usr/bin/env python3
"""
Enhanced cleanup script for redundant test files across all test categories.

This script extends the previous cleanup to handle:
- Unit tests (already done)
- Feature tests
- Integration tests

Safely backs up and removes redundant files while preserving functionality.
"""

import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set

# ANSI colors for better output
class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text: str) -> None:
    """Print a formatted header."""
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*70}")
    print(f"{text:^70}")
    print(f"{'='*70}{Colors.END}")

def print_success(text: str) -> None:
    """Print success message."""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_warning(text: str) -> None:
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_error(text: str) -> None:
    """Print error message."""
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_info(text: str) -> None:
    """Print info message."""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

# Redundant files to be removed, organized by category
REDUNDANT_FILES = {
    "feature": [
        "tests/feature/test_include_processing_features.py",
        "tests/feature/test_include_processing_enhanced_features.py",
        "tests/feature/test_include_processing_integration.py",
        "tests/feature/test_include_dependency_processing.py"
    ],
    "integration": [
        "tests/integration/test_include_processing_comprehensive.py",
        "tests/integration/test_parser_tokenizer_integration.py"
    ]
}

# Consolidated files that should be preserved
CONSOLIDATED_FILES = [
    "tests/unit/test_include_processing_consolidated.py",
    "tests/feature/test_include_processing_consolidated_features.py",
    "tests/integration/test_consolidated_integration.py",
    "tests/utils.py",
    "tests/conftest.py"
]

def analyze_file_relationships() -> Dict[str, List[str]]:
    """Analyze which files might have dependencies."""
    relationships = {
        "feature_consolidation": {
            "source_files": REDUNDANT_FILES["feature"],
            "consolidated_into": "tests/feature/test_include_processing_consolidated_features.py",
            "estimated_lines_removed": 2935  # Based on file sizes we saw
        },
        "integration_consolidation": {
            "source_files": REDUNDANT_FILES["integration"],
            "consolidated_into": "tests/integration/test_consolidated_integration.py", 
            "estimated_lines_removed": 1095  # Based on file sizes
        }
    }
    return relationships

def get_file_stats(file_path: Path) -> Dict[str, int]:
    """Get statistics about a file."""
    if not file_path.exists():
        return {"lines": 0, "size": 0}
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = len(f.readlines())
        size = file_path.stat().st_size
        return {"lines": lines, "size": size}
    except Exception:
        return {"lines": 0, "size": 0}

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

def remove_file(file_path: str) -> bool:
    """Remove a file."""
    try:
        os.remove(file_path)
        print_success(f"Removed: {file_path}")
        return True
    except Exception as e:
        print_error(f"Failed to remove {file_path}: {e}")
        return False

def create_backup_directory() -> Path:
    """Create a timestamped backup directory."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path(f"test_backups_enhanced_{timestamp}")
    backup_dir.mkdir(exist_ok=True)
    print_success(f"Created backup directory: {backup_dir}")
    return backup_dir

def generate_enhanced_report(backup_dir: Path, removed_files: List[str], 
                           total_lines_removed: int) -> None:
    """Generate an enhanced cleanup report."""
    report_file = backup_dir / "enhanced_cleanup_report.md"
    
    relationships = analyze_file_relationships()
    
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("# Enhanced Test Cleanup Report\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## Summary\n\n")
        f.write("This report documents the enhanced cleanup of redundant test files ")
        f.write("across unit, feature, and integration test categories. ")
        f.write("The files listed below have been consolidated into organized test modules ")
        f.write("to reduce duplication and improve maintainability.\n\n")
        
        f.write("## Files Removed by Category\n\n")
        
        # Group removed files by category
        feature_files = []
        integration_files = []
        
        for file_path in removed_files:
            if "/feature/" in file_path:
                feature_files.append(file_path)
            elif "/integration/" in file_path:
                integration_files.append(file_path)
        
        if feature_files:
            f.write("### Feature Tests\n\n")
            for file_path in feature_files:
                stats = get_file_stats(Path(file_path))
                f.write(f"- `{file_path}` ({stats['lines']} lines)\n")
            f.write("\n")
        
        if integration_files:
            f.write("### Integration Tests\n\n")
            for file_path in integration_files:
                stats = get_file_stats(Path(file_path))
                f.write(f"- `{file_path}` ({stats['lines']} lines)\n")
            f.write("\n")
        
        f.write("## Consolidated Into\n\n")
        for consolidated_file in CONSOLIDATED_FILES:
            if Path(consolidated_file).exists():
                stats = get_file_stats(Path(consolidated_file))
                f.write(f"- `{consolidated_file}` ({stats['lines']} lines)\n")
        f.write("\n")
        
        f.write("## Consolidation Details\n\n")
        for category, details in relationships.items():
            f.write(f"### {category.replace('_', ' ').title()}\n\n")
            f.write(f"**Consolidated into:** `{details['consolidated_into']}`\n\n")
            f.write("**Source files:**\n")
            for source_file in details['source_files']:
                f.write(f"- `{source_file}`\n")
            f.write(f"\n**Estimated lines removed:** {details['estimated_lines_removed']}\n\n")
        
        f.write("## Benefits\n\n")
        f.write("- Reduced code duplication across test categories\n")
        f.write("- Improved test organization and discoverability\n")
        f.write("- Better test isolation and reusability\n")
        f.write("- Shared test utilities and consistent patterns\n")
        f.write("- Easier maintenance and updates\n")
        f.write("- Faster test discovery and execution\n\n")
        
        f.write(f"## Statistics\n\n")
        f.write(f"- **Total files removed:** {len(removed_files)}\n")
        f.write(f"- **Estimated lines removed:** {total_lines_removed}\n")
        f.write(f"- **Backup location:** `{backup_dir}`\n\n")
        
        f.write("## Recovery\n\n")
        f.write("If any functionality was accidentally removed, the original files ")
        f.write(f"are backed up in this directory: `{backup_dir}`\n\n")
        
        f.write("To restore a file:\n")
        f.write("```bash\n")
        f.write(f"cp {backup_dir}/path/to/file original/location/\n")
        f.write("```\n\n")
        
        f.write("## Testing\n\n")
        f.write("After cleanup, verify everything works:\n")
        f.write("```bash\n")
        f.write("python3 run_all_tests.py --stats\n")
        f.write("```\n")

def check_consolidated_files_exist() -> bool:
    """Check that all consolidated files exist."""
    missing_files = []
    for file_path in CONSOLIDATED_FILES:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print_error("Missing consolidated files:")
        for file_path in missing_files:
            print_error(f"  - {file_path}")
        return False
    
    return True

def get_total_estimated_lines() -> int:
    """Calculate total estimated lines to be removed."""
    total = 0
    relationships = analyze_file_relationships()
    for details in relationships.values():
        total += details["estimated_lines_removed"]
    return total

def main():
    """Main cleanup function."""
    print_header("🧹 Enhanced Test Suite Cleanup")
    
    print_info("This script will help clean up redundant test files across all categories.")
    print_info("All files will be backed up before removal.")
    
    # Check if consolidated files exist
    if not check_consolidated_files_exist():
        print_error("Cannot proceed without consolidated files. Please create them first.")
        return False
    
    # Analyze files to be removed
    all_redundant_files = []
    for category, files in REDUNDANT_FILES.items():
        all_redundant_files.extend(files)
    
    # Check which files actually exist
    existing_files = []
    for file_path in all_redundant_files:
        if Path(file_path).exists():
            existing_files.append(file_path)
    
    if not existing_files:
        print_info("No redundant files found to clean up.")
        return True
    
    print_info("Redundant files identified:")
    feature_count = 0
    integration_count = 0
    
    for file_path in existing_files:
        stats = get_file_stats(Path(file_path))
        if "/feature/" in file_path:
            feature_count += 1
            print_info(f"  [FEATURE] {file_path} ({stats['lines']} lines)")
        elif "/integration/" in file_path:
            integration_count += 1
            print_info(f"  [INTEGRATION] {file_path} ({stats['lines']} lines)")
    
    total_estimated_lines = get_total_estimated_lines()
    
    print()
    print_info(f"Files to be removed:")
    print_info(f"  - Feature tests: {feature_count}")
    print_info(f"  - Integration tests: {integration_count}")
    print_info(f"  - Total: {len(existing_files)}")
    print_info(f"  - Estimated lines removed: {total_estimated_lines}")
    
    print()
    response = input(f"{Colors.YELLOW}Do you want to proceed with enhanced cleanup? (y/N): {Colors.END}")
    if response.lower() != 'y':
        print_info("Cleanup cancelled.")
        return True
    
    # Create backup directory
    backup_dir = create_backup_directory()
    
    print_header("📦 Backing Up Files")
    backup_success = True
    for file_path in existing_files:
        if not backup_file(file_path, backup_dir):
            backup_success = False
    
    if not backup_success:
        print_error("Some files failed to backup. Aborting cleanup.")
        return False
    
    print_header("🗑️  Removing Redundant Files")
    removed_files = []
    for file_path in existing_files:
        if remove_file(file_path):
            removed_files.append(file_path)
    
    print_header("📊 Generating Report")
    generate_enhanced_report(backup_dir, removed_files, total_estimated_lines)
    print_success(f"Enhanced cleanup report generated: {backup_dir}/enhanced_cleanup_report.md")
    
    print_header("✨ Enhanced Cleanup Complete")
    print_success(f"Files backed up: {len(removed_files)}")
    print_success(f"Files removed: {len(removed_files)}")
    print_success(f"Estimated lines removed: {total_estimated_lines}")
    print_success(f"Backup location: {backup_dir}")
    print_info("Run tests to verify everything still works:")
    print_info("  python3 run_all_tests.py --stats")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print_warning("\nCleanup interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)