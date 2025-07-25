#!/usr/bin/env python3
"""
Generate detailed coverage report with code context.
This script creates a markdown file showing uncovered code lines with context.
"""

import coverage
import os
import sys
from pathlib import Path


def generate_detailed_coverage_report():
    """Generate a detailed coverage report with code context."""
    
    # Initialize coverage
    cov = coverage.Coverage()
    
    try:
        cov.load()
    except coverage.misc.CoverageException:
        print("No coverage data found. Run tests with coverage first.")
        return False
    
    # Get coverage data
    analysis = cov.analysis2()
    
    # Create detailed coverage report
    report_lines = []
    report_lines.append('# Detailed Coverage Report')
    report_lines.append('')
    report_lines.append('This report shows all uncovered code lines with context, highlighting which lines are covered and which are not.')
    report_lines.append('')
    report_lines.append('## Coverage Summary')
    report_lines.append('')
    
    # Get overall stats
    total_statements = sum(len(stmts) for stmts, _, _, _ in analysis.values())
    total_missing = sum(len(missing) for _, _, missing, _ in analysis.values())
    total_coverage = ((total_statements - total_missing) / total_statements * 100) if total_statements > 0 else 0
    
    report_lines.append(f'- **Total Coverage:** {total_coverage:.2f}%')
    report_lines.append(f'- **Total Statements:** {total_statements:,}')
    report_lines.append(f'- **Missing Statements:** {total_missing:,}')
    report_lines.append(f'- **Files with Coverage Issues:** {len([f for f, (stmts, _, missing, _) in analysis.items() if missing])}')
    report_lines.append('')
    
    # Process each file
    for filename, (statements, excluded, missing, missing_branches) in analysis.items():
        if not missing:  # Skip files with 100% coverage
            continue
            
        # Calculate file coverage
        file_coverage = ((len(statements) - len(missing)) / len(statements) * 100) if statements else 0
        covered_count = len(statements) - len(missing)
        
        report_lines.append('---')
        report_lines.append('')
        report_lines.append(f'## File: {filename}')
        report_lines.append(f'**Coverage:** {file_coverage:.2f}% ({covered_count}/{len(statements)} lines covered)')
        report_lines.append('')
        report_lines.append('### Uncovered Lines with Context')
        report_lines.append('')
        
        # Read the source file
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                source_lines = f.readlines()
        except Exception as e:
            report_lines.append(f'*Unable to read source file: {filename} - {e}*')
            continue
        
        # Group missing lines into ranges
        missing_ranges = []
        if missing:
            missing_list = sorted(missing)
            start = missing_list[0]
            end = start
            
            for line_num in missing_list[1:]:
                if line_num == end + 1:
                    end = line_num
                else:
                    missing_ranges.append((start, end))
                    start = end = line_num
            missing_ranges.append((start, end))
        
        # Show context for each missing range
        for start_line, end_line in missing_ranges:
            if start_line == end_line:
                report_lines.append(f'#### Line {start_line}')
            else:
                report_lines.append(f'#### Lines {start_line}-{end_line}')
            
            report_lines.append('```python')
            
            # Show context (3 lines before and after)
            context_start = max(1, start_line - 3)
            context_end = min(len(source_lines), end_line + 3)
            
            for i in range(context_start, context_end + 1):
                line_content = source_lines[i-1].rstrip()
                
                if i < start_line or i > end_line:
                    # This is context (covered or outside missing range)
                    report_lines.append(f'# Line {i}: {line_content}')
                else:
                    # This is a missing line
                    report_lines.append(f'# Line {i}: ❌ NOT COVERED')
                    report_lines.append(f'{line_content}')
            
            report_lines.append('```')
            report_lines.append('')
        
        # Add summary of all missing lines if there are many
        if len(missing) > 10:
            report_lines.append('#### Additional Missing Lines')
            report_lines.append('```python')
            report_lines.append('# Additional uncovered lines:')
            for line_num in sorted(missing):
                report_lines.append(f'# Line {line_num}: ❌ NOT COVERED')
            report_lines.append('```')
            report_lines.append('')
    
    # Add legend and recommendations
    report_lines.append('---')
    report_lines.append('')
    report_lines.append('## Legend')
    report_lines.append('')
    report_lines.append('- ✅ **Covered lines**: Code that was executed during testing')
    report_lines.append('- ❌ **NOT COVERED**: Code that was not executed during testing')
    report_lines.append('- **Context lines**: Code before and after uncovered lines to provide understanding')
    report_lines.append('')
    report_lines.append('## Recommendations')
    report_lines.append('')
    
    # Find files with lowest coverage
    file_coverage_data = []
    for filename, (statements, excluded, missing, missing_branches) in analysis.items():
        if statements:
            coverage_pct = ((len(statements) - len(missing)) / len(statements) * 100)
            file_coverage_data.append((filename, coverage_pct, len(missing)))
    
    # Sort by coverage (lowest first)
    file_coverage_data.sort(key=lambda x: x[1])
    
    if file_coverage_data:
        report_lines.append('1. **Focus on low coverage files**:')
        for filename, coverage_pct, missing_count in file_coverage_data[:3]:
            report_lines.append(f'   - {filename}: {coverage_pct:.2f}% coverage ({missing_count} missing lines)')
        report_lines.append('')
        report_lines.append('2. **Add edge case tests**: Many uncovered lines appear to be error handling and edge cases')
        report_lines.append('3. **Test command-line interface**: The main function and argument parsing are largely uncovered')
    
    # Write the report
    output_file = 'tests/reports/coverage.md'
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    
    print(f'✅ Detailed coverage report generated: {output_file}')
    return True


if __name__ == '__main__':
    success = generate_detailed_coverage_report()
    sys.exit(0 if success else 1)