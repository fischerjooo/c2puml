#!/usr/bin/env python3
"""
Generate test summary report.
This script creates a markdown file with test execution statistics and coverage summary.
"""

import os
import sys
import re
from pathlib import Path


def extract_test_statistics(test_results_file):
    """Extract test statistics from test results file."""
    stats = {}
    
    try:
        with open(test_results_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract statistics using regex
        stats_pattern = r'Total test files:\s*(\d+)'
        unit_pattern = r'Unit tests:\s*(\d+)'
        feature_pattern = r'Feature tests:\s*(\d+)'
        integration_pattern = r'Integration tests:\s*(\d+)'
        lines_pattern = r'Total lines of test code:\s*(\d+)'
        
        stats['total_files'] = re.search(stats_pattern, content)
        stats['unit_tests'] = re.search(unit_pattern, content)
        stats['feature_tests'] = re.search(feature_pattern, content)
        stats['integration_tests'] = re.search(integration_pattern, content)
        stats['test_lines'] = re.search(lines_pattern, content)
        
        # Extract actual values
        for key, match in stats.items():
            if match:
                stats[key] = match.group(1)
            else:
                stats[key] = '0'
                
    except FileNotFoundError:
        print(f"Warning: Test results file not found: {test_results_file}")
        stats = {
            'total_files': '0',
            'unit_tests': '0',
            'feature_tests': '0',
            'integration_tests': '0',
            'test_lines': '0'
        }
    except Exception as e:
        print(f"Error reading test results file: {e}")
        stats = {
            'total_files': '0',
            'unit_tests': '0',
            'feature_tests': '0',
            'integration_tests': '0',
            'test_lines': '0'
        }
    
    return stats


def extract_coverage_summary(coverage_summary_file):
    """Extract coverage summary from coverage report file."""
    coverage_data = {}
    
    try:
        with open(coverage_summary_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Find the TOTAL line
        for line in lines:
            if line.strip().startswith('TOTAL'):
                parts = line.strip().split()
                if len(parts) >= 4:
                    coverage_data['total_statements'] = parts[1]
                    coverage_data['missing_statements'] = parts[2]
                    coverage_data['coverage_percentage'] = parts[3]
                    break
                    
    except FileNotFoundError:
        print(f"Warning: Coverage summary file not found: {coverage_summary_file}")
        coverage_data = {
            'total_statements': '0',
            'missing_statements': '0',
            'coverage_percentage': '0.00%'
        }
    except Exception as e:
        print(f"Error reading coverage summary file: {e}")
        coverage_data = {
            'total_statements': '0',
            'missing_statements': '0',
            'coverage_percentage': '0.00%'
        }
    
    return coverage_data


def generate_test_summary_report():
    """Generate the test summary report."""
    
    # File paths
    test_results_file = 'tests/reports/test-results.txt'
    coverage_summary_file = 'tests/reports/coverage-summary.txt'
    output_file = 'tests/reports/summary.md'
    
    # Extract data
    test_stats = extract_test_statistics(test_results_file)
    coverage_data = extract_coverage_summary(coverage_summary_file)
    
    # Create report
    report_lines = []
    report_lines.append('# Test Results Summary')
    report_lines.append('')
    report_lines.append('## Test Execution Statistics')
    report_lines.append('')
    
    # Add test suite overview if we have test results
    if test_stats['total_files'] != '0':
        report_lines.append('### Test Suite Overview')
        report_lines.append('```')
        report_lines.append('--------------------------------------------------')
        report_lines.append('              Test Suite Statistics               ')
        report_lines.append('--------------------------------------------------')
        report_lines.append(f'Total test files: {test_stats["total_files"]}')
        report_lines.append(f'Unit tests: {test_stats["unit_tests"]}')
        report_lines.append(f'Feature tests: {test_stats["feature_tests"]}')
        report_lines.append(f'Integration tests: {test_stats["integration_tests"]}')
        report_lines.append(f'Total lines of test code: {test_stats["test_lines"]}')
        report_lines.append('```')
        report_lines.append('')
    
    # Add coverage summary if available
    if coverage_data['coverage_percentage'] != '0.00%':
        report_lines.append('### Code Coverage Report')
        report_lines.append('```')
        
        try:
            with open(coverage_summary_file, 'r', encoding='utf-8') as f:
                coverage_content = f.read()
                report_lines.append(coverage_content.strip())
        except FileNotFoundError:
            report_lines.append('Coverage data not available')
        
        report_lines.append('```')
        report_lines.append('')
    
    # Add overall results
    report_lines.append('### Overall Results')
    
    if coverage_data['coverage_percentage'] != '0.00%':
        report_lines.append(f'- **Overall Coverage:** {coverage_data["coverage_percentage"]}')
    
    if test_stats['total_files'] != '0':
        report_lines.append(f'- **Total Test Files:** {test_stats["total_files"]}')
        report_lines.append(f'- **Unit Tests:** {test_stats["unit_tests"]}')
        report_lines.append(f'- **Feature Tests:** {test_stats["feature_tests"]}')
        report_lines.append(f'- **Integration Tests:** {test_stats["integration_tests"]}')
    
    # Add link to detailed coverage report if it exists
    coverage_detail_file = 'tests/reports/coverage.md'
    if os.path.exists(coverage_detail_file):
        report_lines.append('')
        report_lines.append('📊 **[View Detailed Coverage Report](coverage.md)** - See uncovered code lines with context')
    
    # Write the report
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    
    print(f'✅ Test summary report generated: {output_file}')
    return True


if __name__ == '__main__':
    success = generate_test_summary_report()
    sys.exit(0 if success else 1)