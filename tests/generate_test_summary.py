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
    """Generate HTML header with CSS styling."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Results Summary</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-bottom: 30px;
        }
        h2 {
            color: #34495e;
            margin-top: 30px;
            margin-bottom: 15px;
        }
        h3 {
            color: #7f8c8d;
            margin-top: 25px;
            margin-bottom: 10px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .stat-label {
            font-size: 0.9em;
            opacity: 0.9;
        }
        .coverage-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background-color: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .coverage-table th {
            background-color: #34495e;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }
        .coverage-table td {
            padding: 10px 12px;
            border-bottom: 1px solid #ecf0f1;
        }
        .coverage-table tr:hover {
            background-color: #f8f9fa;
        }
        .coverage-high {
            color: #27ae60;
            font-weight: bold;
        }
        .coverage-medium {
            color: #f39c12;
            font-weight: bold;
        }
        .coverage-low {
            color: #e74c3c;
            font-weight: bold;
        }
        .link-button {
            display: inline-block;
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: white;
            padding: 12px 24px;
            text-decoration: none;
            border-radius: 6px;
            margin: 20px 0;
            transition: transform 0.2s;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .link-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        .test-stats {
            background-color: #ecf0f1;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            font-family: 'Courier New', monospace;
            white-space: pre;
            overflow-x: auto;
        }
        .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ecf0f1;
            text-align: center;
            color: #7f8c8d;
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
    output_file = 'tests/reports/summary.html'
    
    # Extract data
    test_stats = extract_test_statistics(test_results_file)
    coverage_data = extract_coverage_summary(coverage_summary_file)
    
    # Start building HTML
    html_content = [generate_html_header()]
    
    # Title
    html_content.append('<h1>🧪 Test Results Summary</h1>')
    
    # Overall stats grid
    html_content.append('<div class="stats-grid">')
    
    if coverage_data['coverage_percentage'] != '0.00%':
        html_content.append(f'''
        <div class="stat-card">
            <div class="stat-value">{coverage_data["coverage_percentage"]}</div>
            <div class="stat-label">Overall Coverage</div>
        </div>''')
    
    if test_stats['total_files'] != '0':
        html_content.append(f'''
        <div class="stat-card">
            <div class="stat-value">{test_stats["total_files"]}</div>
            <div class="stat-label">Total Test Files</div>
        </div>''')
        
        html_content.append(f'''
        <div class="stat-card">
            <div class="stat-value">{test_stats["unit_tests"]}</div>
            <div class="stat-label">Unit Tests</div>
        </div>''')
        
        html_content.append(f'''
        <div class="stat-card">
            <div class="stat-value">{test_stats["feature_tests"]}</div>
            <div class="stat-label">Feature Tests</div>
        </div>''')
        
        html_content.append(f'''
        <div class="stat-card">
            <div class="stat-value">{test_stats["integration_tests"]}</div>
            <div class="stat-label">Integration Tests</div>
        </div>''')
    
    html_content.append('</div>')
    
    # Test suite overview
    if test_stats['total_files'] != '0':
        html_content.append('<h2>📊 Test Suite Overview</h2>')
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
        html_content.append('<h2>📈 Code Coverage Report</h2>')
        
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
                        
                        # Determine coverage class
                        if coverage == '100.00%':
                            coverage_class = 'coverage-high'
                        elif float(coverage.replace('%', '')) >= 80:
                            coverage_class = 'coverage-medium'
                        else:
                            coverage_class = 'coverage-low'
                        
                        html_content.append(f'<td>{filename}</td>')
                        html_content.append(f'<td>{statements}</td>')
                        html_content.append(f'<td>{missing}</td>')
                        html_content.append(f'<td class="{coverage_class}">{coverage}</td>')
                        html_content.append(f'<td style="font-family: monospace; font-size: 0.9em;">{missing_lines}</td>')
                        html_content.append('</tr>')
            
            html_content.append('</tbody></table>')
            
        except FileNotFoundError:
            html_content.append('<p>Coverage data not available</p>')
    
    # Link to detailed coverage report
    coverage_detail_file = 'tests/reports/coverage.html'
    if os.path.exists(coverage_detail_file):
        html_content.append('<h2>🔍 Detailed Analysis</h2>')
        html_content.append('<a href="coverage.html" class="link-button">📊 View Detailed Coverage Report</a>')
        html_content.append('<p>See uncovered code lines with context and background coloring</p>')
    
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