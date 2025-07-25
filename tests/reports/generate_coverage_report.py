#!/usr/bin/env python3
"""
Generate detailed coverage report in HTML format with code context.
This script creates an HTML file showing uncovered code lines with context and background coloring.
"""

import coverage
import os
import sys
from pathlib import Path


def generate_html_header():
    """Generate HTML header with CSS styling."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Detailed Coverage Report</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1400px;
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
            padding: 10px;
            background-color: #ecf0f1;
            border-radius: 5px;
        }
        h3 {
            color: #7f8c8d;
            margin-top: 25px;
            margin-bottom: 10px;
        }
        h4 {
            color: #e74c3c;
            margin-top: 20px;
            margin-bottom: 10px;
            font-family: 'Courier New', monospace;
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
        .file-section {
            margin: 30px 0;
            padding: 20px;
            border: 1px solid #ecf0f1;
            border-radius: 8px;
            background-color: #fafafa;
        }
        .file-header {
            background: linear-gradient(135deg, #34495e, #2c3e50);
            color: white;
            padding: 15px;
            margin: -20px -20px 20px -20px;
            border-radius: 8px 8px 0 0;
            font-weight: bold;
        }
        .coverage-info {
            display: inline-block;
            background-color: #3498db;
            color: white;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.9em;
            margin-left: 10px;
        }
        .code-block {
            background-color: #2d3748;
            color: #e2e8f0;
            padding: 20px;
            border-radius: 8px;
            margin: 15px 0;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            line-height: 1.4;
            overflow-x: auto;
            white-space: pre;
        }
        .line-number {
            display: inline-block;
            width: 50px;
            color: #718096;
            text-align: right;
            margin-right: 15px;
            user-select: none;
        }
        .line-covered {
            background-color: #d4edda;
            color: #155724;
        }
        .line-uncovered {
            background-color: #f8d7da;
            color: #721c24;
        }
        .line-context {
            background-color: #f8f9fa;
            color: #6c757d;
        }
        .legend {
            background-color: #ecf0f1;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }
        .legend-item {
            display: flex;
            align-items: center;
            margin: 10px 0;
        }
        .legend-color {
            width: 20px;
            height: 20px;
            margin-right: 10px;
            border-radius: 3px;
        }
        .recommendations {
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }
        .recommendations h3 {
            color: #856404;
            margin-top: 0;
        }
        .recommendations ul {
            color: #856404;
        }
        .back-link {
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
        .back-link:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
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


def generate_detailed_coverage_report():
    """Generate a detailed coverage report with code context in HTML format."""
    
    # Initialize coverage
    cov = coverage.Coverage()
    
    try:
        cov.load()
    except coverage.misc.CoverageException:
        print("No coverage data found. Run tests with coverage first.")
        return False
    
    # Get coverage data
    analysis = cov.analysis2()
    
    # Start building HTML
    html_content = [generate_html_header()]
    
    # Title
    html_content.append('<h1>📊 Detailed Coverage Report</h1>')
    html_content.append('<p>This report shows all uncovered code lines with context, highlighting which lines are covered and which are not.</p>')
    
    # Overall stats
    total_statements = sum(len(stmts) for stmts, _, _, _ in analysis.values())
    total_missing = sum(len(missing) for _, _, missing, _ in analysis.values())
    total_coverage = ((total_statements - total_missing) / total_statements * 100) if total_statements > 0 else 0
    files_with_issues = len([f for f, (stmts, _, missing, _) in analysis.items() if missing])
    
    html_content.append('<div class="stats-grid">')
    html_content.append(f'''
    <div class="stat-card">
        <div class="stat-value">{total_coverage:.2f}%</div>
        <div class="stat-label">Total Coverage</div>
    </div>''')
    html_content.append(f'''
    <div class="stat-card">
        <div class="stat-value">{total_statements:,}</div>
        <div class="stat-label">Total Statements</div>
    </div>''')
    html_content.append(f'''
    <div class="stat-card">
        <div class="stat-value">{total_missing:,}</div>
        <div class="stat-label">Missing Statements</div>
    </div>''')
    html_content.append(f'''
    <div class="stat-card">
        <div class="stat-value">{files_with_issues}</div>
        <div class="stat-label">Files with Issues</div>
    </div>''')
    html_content.append('</div>')
    
    # Legend
    html_content.append('<div class="legend">')
    html_content.append('<h3>📋 Legend</h3>')
    html_content.append('<div class="legend-item">')
    html_content.append('<div class="legend-color" style="background-color: #d4edda;"></div>')
    html_content.append('<span>✅ Covered lines: Code that was executed during testing</span>')
    html_content.append('</div>')
    html_content.append('<div class="legend-item">')
    html_content.append('<div class="legend-color" style="background-color: #f8d7da;"></div>')
    html_content.append('<span>❌ Uncovered lines: Code that was not executed during testing</span>')
    html_content.append('</div>')
    html_content.append('<div class="legend-item">')
    html_content.append('<div class="legend-color" style="background-color: #f8f9fa;"></div>')
    html_content.append('<span>📝 Context lines: Code before and after uncovered lines for understanding</span>')
    html_content.append('</div>')
    html_content.append('</div>')
    
    # Process each file
    for filename, (statements, excluded, missing, missing_branches) in analysis.items():
        if not missing:  # Skip files with 100% coverage
            continue
            
        # Calculate file coverage
        file_coverage = ((len(statements) - len(missing)) / len(statements) * 100) if statements else 0
        covered_count = len(statements) - len(missing)
        
        html_content.append('<div class="file-section">')
        html_content.append(f'<div class="file-header">')
        html_content.append(f'📁 {filename}')
        html_content.append(f'<span class="coverage-info">{file_coverage:.2f}% ({covered_count}/{len(statements)} lines covered)</span>')
        html_content.append('</div>')
        
        # Read the source file
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                source_lines = f.readlines()
        except Exception as e:
            html_content.append(f'<p><em>Unable to read source file: {filename} - {e}</em></p>')
            html_content.append('</div>')
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
                html_content.append(f'<h4>Line {start_line}</h4>')
            else:
                html_content.append(f'<h4>Lines {start_line}-{end_line}</h4>')
            
            html_content.append('<div class="code-block">')
            
            # Show context (10 lines before and after)
            context_start = max(1, start_line - 10)
            context_end = min(len(source_lines), end_line + 10)
            
            for i in range(context_start, context_end + 1):
                line_content = source_lines[i-1].rstrip()
                
                if i < start_line or i > end_line:
                    # This is context (covered or outside missing range)
                    html_content.append(f'<div class="line-context">')
                    html_content.append(f'<span class="line-number">{i:3d}</span>{line_content}')
                    html_content.append('</div>')
                else:
                    # This is a missing line
                    html_content.append(f'<div class="line-uncovered">')
                    html_content.append(f'<span class="line-number">{i:3d}</span>{line_content}')
                    html_content.append('</div>')
            
            html_content.append('</div>')
        
        html_content.append('</div>')
    
    # Recommendations
    html_content.append('<div class="recommendations">')
    html_content.append('<h3>💡 Recommendations</h3>')
    
    # Find files with lowest coverage
    file_coverage_data = []
    for filename, (statements, excluded, missing, missing_branches) in analysis.items():
        if statements:
            coverage_pct = ((len(statements) - len(missing)) / len(statements) * 100)
            file_coverage_data.append((filename, coverage_pct, len(missing)))
    
    # Sort by coverage (lowest first)
    file_coverage_data.sort(key=lambda x: x[1])
    
    if file_coverage_data:
        html_content.append('<ul>')
        html_content.append('<li><strong>Focus on low coverage files:</strong>')
        html_content.append('<ul>')
        for filename, coverage_pct, missing_count in file_coverage_data[:3]:
            html_content.append(f'<li>{filename}: {coverage_pct:.2f}% coverage ({missing_count} missing lines)</li>')
        html_content.append('</ul></li>')
        html_content.append('<li><strong>Add edge case tests:</strong> Many uncovered lines appear to be error handling and edge cases</li>')
        html_content.append('<li><strong>Test command-line interface:</strong> The main function and argument parsing are largely uncovered</li>')
        html_content.append('</ul>')
    
    html_content.append('</div>')
    
    # Back link
    html_content.append('<a href="summary.html" class="back-link">← Back to Test Summary</a>')
    
    # Footer
    html_content.append(generate_html_footer())
    
    # Write the report
    output_file = 'tests/reports/coverage.html'
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(html_content))
    
    print(f'✅ Detailed coverage report generated: {output_file}')
    return True


if __name__ == '__main__':
    success = generate_detailed_coverage_report()
    sys.exit(0 if success else 1)