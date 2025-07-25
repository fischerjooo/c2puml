#!/usr/bin/env python3
"""
Generate test summary report in HTML format.
This script creates an HTML file with test execution statistics and coverage summary.
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


def generate_html_header():
    """Generate HTML header with minimal, mobile-friendly styling."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Results Summary</title>
    <style>
        body {
            font-family: monospace;
            line-height: 1.4;
            margin: 0;
            padding: 15px;
            background-color: white;
            color: #333;
            font-size: 14px;
        }
        .container {
            max-width: 100%;
            margin: 0;
            padding: 0;
        }
        h1, h2, h3 {
            color: #333;
            font-weight: normal;
            margin: 20px 0 10px 0;
            padding: 0;
            border: none;
            background: none;
            font-family: monospace;
        }
        h1 {
            font-size: 18px;
            border-bottom: 1px solid #ccc;
            padding-bottom: 5px;
        }
        h2 {
            font-size: 16px;
            margin-top: 30px;
        }
        h3 {
            font-size: 14px;
        }
        .stats-list {
            margin: 15px 0;
            padding: 0;
            list-style: none;
        }
        .stats-list li {
            margin: 3px 0;
            padding: 3px 0;
            border-bottom: 1px dotted #ddd;
        }
        .coverage-table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            font-size: 12px;
            font-family: monospace;
        }
        .coverage-table th {
            background-color: #f0f0f0;
            color: #333;
            padding: 6px 4px;
            text-align: left;
            font-weight: normal;
            border: 1px solid #ccc;
        }
        .coverage-table td {
            padding: 4px;
            border: 1px solid #ccc;
            vertical-align: top;
        }
        .coverage-table tr:nth-child(even) {
            background-color: #fafafa;
        }
        .test-stats {
            background-color: #f8f8f8;
            padding: 10px;
            margin: 15px 0;
            border: 1px solid #ddd;
            font-family: monospace;
            white-space: pre;
            overflow-x: auto;
            font-size: 12px;
        }
        .nav-links {
            margin: 20px 0;
            padding: 15px 0;
            border-top: 1px solid #ccc;
            border-bottom: 1px solid #ccc;
        }
        .nav-links h3 {
            margin: 0 0 10px 0;
        }
        .nav-links a {
            display: block;
            color: #0066cc;
            text-decoration: none;
            margin: 5px 0;
            padding: 3px 0;
        }
        .nav-links a:hover {
            text-decoration: underline;
        }
        .footer {
            margin-top: 30px;
            padding-top: 15px;
            border-top: 1px solid #ccc;
            font-size: 12px;
            color: #666;
            text-align: center;
        }
        @media (max-width: 768px) {
            body {
                padding: 8px;
                font-size: 13px;
            }
            .coverage-table {
                font-size: 10px;
            }
            .coverage-table th,
            .coverage-table td {
                padding: 2px;
            }
            .test-stats {
                font-size: 10px;
                padding: 8px;
            }
        }
    </style>
</head>
<body>
    <div class="container">"""


def generate_html_footer():
    """Generate HTML footer."""
    return """
    </div>
    <div class="footer">
        <p>Generated by Test Report System</p>
    </div>
</body>
</html>"""


def generate_test_summary_report():
    """Generate the test summary report in HTML format."""
    
    # File paths
    test_results_file = 'tests/reports/test-results.txt'
    coverage_summary_file = 'tests/reports/coverage-summary.txt'
    output_file = 'tests/reports/index.html'
    
    # Extract data
    test_stats = extract_test_statistics(test_results_file)
    coverage_data = extract_coverage_summary(coverage_summary_file)
    
    # Start building HTML
    html_content = [generate_html_header()]
    
    # Title
    html_content.append('<h1>Test Reports Dashboard</h1>')
    
    # Summary Section
    html_content.append('<h2>Test Results Summary</h2>')
    
    # Overall stats list
    html_content.append('<ul class="stats-list">')
    
    if coverage_data['coverage_percentage'] != '0.00%':
        html_content.append(f'<li>Overall Coverage: {coverage_data["coverage_percentage"]}</li>')
    
    if test_stats['total_files'] != '0':
        html_content.append(f'<li>Total Test Files: {test_stats["total_files"]}</li>')
        html_content.append(f'<li>Unit Tests: {test_stats["unit_tests"]}</li>')
        html_content.append(f'<li>Feature Tests: {test_stats["feature_tests"]}</li>')
        html_content.append(f'<li>Integration Tests: {test_stats["integration_tests"]}</li>')
    
    html_content.append('</ul>')
    
    # Test suite overview
    if test_stats['total_files'] != '0':
        html_content.append('<h2>Test Suite Overview</h2>')
        html_content.append('<div class="test-stats">')
        html_content.append('--------------------------------------------------')
        html_content.append('              Test Suite Statistics               ')
        html_content.append('--------------------------------------------------')
        html_content.append(f'Total test files: {test_stats["total_files"]}')
        html_content.append(f'Unit tests: {test_stats["unit_tests"]}')
        html_content.append(f'Feature tests: {test_stats["feature_tests"]}')
        html_content.append(f'Integration tests: {test_stats["integration_tests"]}')
        html_content.append(f'Total lines of test code: {test_stats["test_lines"]}')
        html_content.append('</div>')
    
    # Coverage summary
    if coverage_data['coverage_percentage'] != '0.00%':
        html_content.append('<h2>Code Coverage Report</h2>')
        
        try:
            with open(coverage_summary_file, 'r', encoding='utf-8') as f:
                coverage_lines = f.readlines()
            
            html_content.append('<table class="coverage-table">')
            html_content.append('<thead><tr><th>File</th><th>Statements</th><th>Missing</th><th>Coverage</th><th>Missing Lines</th></tr></thead>')
            html_content.append('<tbody>')
            
            for line in coverage_lines:
                line = line.strip()
                if line and not line.startswith('---') and not line.startswith('Name'):
                    if line.startswith('TOTAL'):
                        html_content.append('<tr style="background-color: #f8f9fa; font-weight: bold;">')
                    else:
                        html_content.append('<tr>')
                    
                    parts = line.split()
                    if len(parts) >= 4:
                        filename = parts[0]
                        statements = parts[1]
                        missing = parts[2]
                        coverage = parts[3]
                        missing_lines = ' '.join(parts[4:]) if len(parts) > 4 else ''
                        
                        html_content.append(f'<td>{filename}</td>')
                        html_content.append(f'<td>{statements}</td>')
                        html_content.append(f'<td>{missing}</td>')
                        html_content.append(f'<td>{coverage}</td>')
                        html_content.append(f'<td style="font-family: monospace; font-size: 0.9em;">{missing_lines}</td>')
                        html_content.append('</tr>')
            
            html_content.append('</tbody></table>')
            
        except FileNotFoundError:
            html_content.append('<p>Coverage data not available</p>')
    
    # Navigation Section
    html_content.append('<div class="nav-links">')
    html_content.append('<h3>Coverage Reports</h3>')
    html_content.append('<a href="coverage-index.html">Coverage Reports Dashboard</a>')
    html_content.append('<a href="coverage-html/index.html">Interactive HTML Coverage</a>')
    html_content.append('</div>')
    
    # Footer
    html_content.append(generate_html_footer())
    
    # Write the report
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(html_content))
    
    print(f'✅ Test summary report generated: {output_file}')
    return True


if __name__ == '__main__':
    success = generate_test_summary_report()
    sys.exit(0 if success else 1)