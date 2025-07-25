#!/usr/bin/env python3
"""
Generate detailed coverage report in HTML format with code context.
This script creates an HTML file showing uncovered code lines with context and background coloring.
"""

import coverage
import os
import sys
from pathlib import Path
from datetime import datetime


def generate_html_header():
    """Generate HTML header with simple CSS styling."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Code Coverage Report</title>
    <style>
        body {
            font-family: sans-serif;
            background-color: #f9f9f9;
            padding: 2rem;
            max-width: 1200px;
            margin: 0 auto;
            line-height: 1.6;
            color: #333;
        }
        
        h1, h2, h3 {
            color: #2c3e50;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin: 2rem 0;
        }
        
        .stat {
            background: white;
            padding: 1rem;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            color: #3498db;
        }
        
        .file-section {
            background: white;
            margin: 1.5rem 0;
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .file-header {
            background: #34495e;
            color: white;
            padding: 0.75rem 1rem;
            margin: -1rem -1rem 1rem -1rem;
            border-radius: 8px 8px 0 0;
            font-weight: bold;
        }
        
        pre {
            background-color: #2d2d2d;
            color: #f8f8f2;
            padding: 1rem;
            border-radius: 8px;
            overflow-x: auto;
            font-family: Consolas, Monaco, 'Courier New', monospace;
            font-size: 0.95rem;
            line-height: 1.5;
            margin: 1rem 0;
        }
        
        code {
            white-space: pre;
        }
        
        .line-number {
            color: #858585;
            margin-right: 1rem;
            user-select: none;
        }
        
        .covered {
            color: #4caf50;
        }
        
        .uncovered {
            color: #f44336;
        }
        
        .legend {
            background: white;
            padding: 1rem;
            border-radius: 8px;
            margin: 1.5rem 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .legend-item {
            display: flex;
            align-items: center;
            margin: 0.5rem 0;
        }
        
        .legend-color {
            width: 20px;
            height: 20px;
            margin-right: 0.5rem;
            border-radius: 3px;
        }
        
        .footer {
            text-align: center;
            margin-top: 2rem;
            padding: 1rem;
            color: #7f8c8d;
            border-top: 1px solid #ecf0f1;
        }
    </style>
</head>
<body>
    <h1>Code Coverage Report</h1>
    <p>Generated on """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>"""


def apply_syntax_highlighting(line_content):
    """Apply basic syntax highlighting to code lines."""
    import re
    
    # Only apply highlighting if line contains code (not just whitespace)
    if not line_content.strip():
        return line_content
    
    # Keywords (most common ones first for efficiency)
    keywords = ['def', 'class', 'import', 'from', 'if', 'else', 'elif', 'for', 'while', 'try', 'except', 'finally', 'with', 'as', 'return', 'yield', 'break', 'continue', 'pass', 'raise', 'assert', 'del', 'global', 'nonlocal', 'lambda', 'True', 'False', 'None', 'and', 'or', 'not', 'in', 'is']
    for keyword in keywords:
        if keyword in line_content:
            line_content = re.sub(r'\b' + re.escape(keyword) + r'\b', f'<span class="keyword">{keyword}</span>', line_content)
    
    # Comments (check first to avoid highlighting keywords in comments)
    if '#' in line_content:
        line_content = re.sub(r'#.*$', lambda m: f'<span class="comment">{m.group(0)}</span>', line_content)
    
    # Strings (only if not already in a comment)
    if '"' in line_content and 'comment' not in line_content:
        line_content = re.sub(r'"[^"]*"', lambda m: f'<span class="string">{m.group(0)}</span>', line_content)
    if "'" in line_content and 'comment' not in line_content:
        line_content = re.sub(r"'[^']*'", lambda m: f'<span class="string">{m.group(0)}</span>', line_content)
    
    # Numbers (only if not in strings or comments)
    if any(c.isdigit() for c in line_content) and 'string' not in line_content and 'comment' not in line_content:
        line_content = re.sub(r'\b\d+\b', lambda m: f'<span class="number">{m.group(0)}</span>', line_content)
    
    # Function calls (only if not in strings or comments)
    if '(' in line_content and 'string' not in line_content and 'comment' not in line_content:
        line_content = re.sub(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', r'<span class="function">\1</span>(', line_content)
    
    return line_content


def generate_html_footer():
    """Generate HTML footer."""
    return """
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
    analysis = {}
    for filename in cov.get_data().measured_files():
        try:
            result = cov.analysis2(filename)
            # analysis2 returns (filename, statements, excluded, missing, missing_branches)
            analysis[filename] = result
        except Exception as e:
            print(f"Warning: Could not analyze {filename}: {e}")
            continue
    
    # Start building HTML
    html_content = [generate_html_header()]
    
    # Title
    html_content.append('<h1>📊 Detailed Coverage Report</h1>')
    html_content.append('<p>This report shows all uncovered code lines with context, highlighting which lines are covered and which are not.</p>')
    
    # Overall stats
    total_statements = sum(len(stmts) for _, stmts, _, missing, _ in analysis.values())
    total_missing = sum(len(missing) for _, _, _, missing, _ in analysis.values())
    total_coverage = ((total_statements - total_missing) / total_statements * 100) if total_statements > 0 else 0
    files_with_issues = len([f for f, (_, _, _, missing, _) in analysis.items() if missing])
    
    html_content.append('<div class="stats">')
    html_content.append(f'''
    <div class="stat">
        <div class="stat-number">{total_coverage:.2f}%</div>
        <div class="stat-label">Total Coverage</div>
    </div>''')
    html_content.append(f'''
    <div class="stat">
        <div class="stat-number">{total_statements:,}</div>
        <div class="stat-label">Total Statements</div>
    </div>''')
    html_content.append(f'''
    <div class="stat">
        <div class="stat-number">{total_missing:,}</div>
        <div class="stat-label">Missing Statements</div>
    </div>''')
    html_content.append(f'''
    <div class="stat">
        <div class="stat-number">{files_with_issues}</div>
        <div class="stat-label">Files with Issues</div>
    </div>''')
    html_content.append('</div>')
    
    # Legend
    html_content.append('<div class="legend">')
    html_content.append('<h3>Legend</h3>')
    html_content.append('<div class="legend-item">')
    html_content.append('<div class="legend-color" style="background-color: #4caf50;"></div>')
    html_content.append('<span>Covered lines: Code that was executed during testing</span>')
    html_content.append('</div>')
    html_content.append('<div class="legend-item">')
    html_content.append('<div class="legend-color" style="background-color: #f44336;"></div>')
    html_content.append('<span>Uncovered lines: Code that was not executed during testing</span>')
    html_content.append('</div>')
    html_content.append('<div class="legend-item">')
    html_content.append('<div class="legend-color" style="background-color: #858585;"></div>')
    html_content.append('<span>Context lines: Code before and after uncovered lines</span>')
    html_content.append('</div>')
    html_content.append('</div>')
    
    # Process each file
    for filename, (_, statements, excluded, missing, missing_branches) in analysis.items():
        if not missing:  # Skip files with 100% coverage
            continue
            
        # Skip files with very high coverage (>95%) to make report more compact
        coverage_pct = ((len(statements) - len(missing)) / len(statements) * 100) if statements else 0
        if coverage_pct > 95:
            continue
            
        # Calculate file coverage
        file_coverage = ((len(statements) - len(missing)) / len(statements) * 100) if statements else 0
        covered_count = len(statements) - len(missing)
        
        html_content.append('<div class="file-section">')
        html_content.append(f'<div class="file-header">')
        html_content.append(f'{filename} - {file_coverage:.2f}% coverage ({covered_count}/{len(statements)} lines)')
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
            
            html_content.append('<pre>')
            
            # Show context (5 lines before and after for more compact view)
            context_start = max(1, start_line - 5)
            context_end = min(len(source_lines), end_line + 5)
            
            for i in range(context_start, context_end + 1):
                line_content = source_lines[i-1].rstrip()
                highlighted_content = apply_syntax_highlighting(line_content)
                
                if i < start_line or i > end_line:
                    # This is context (covered or outside missing range)
                    html_content.append(f'<span class="line-number">{i:3d}</span>{highlighted_content}')
                else:
                    # This is a missing line
                    html_content.append(f'<span class="line-number">{i:3d}</span><span class="uncovered">{highlighted_content}</span>')
            
            html_content.append('</pre>')
        
        html_content.append('</div>')
    

    
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