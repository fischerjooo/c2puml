#!/usr/bin/env python3
"""
Generate detailed coverage report in HTML format with code context.
This script creates an HTML file showing uncovered code lines with improved styling
and complete function context.
"""

import coverage
import os
import sys
from pathlib import Path
from datetime import datetime
import html
import re
import ast


def generate_html_header():
    """Generate HTML header with improved CSS styling."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Code Coverage Report</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            margin: 0;
            line-height: 1.6;
            color: #333;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #2c3e50, #3498db);
            color: white;
            padding: 2rem;
            text-align: center;
        }
        
        .header h1 {
            margin: 0;
            font-size: 2.5rem;
            font-weight: 300;
        }
        
        .header p {
            margin: 0.5rem 0 0 0;
            opacity: 0.9;
            font-size: 1.1rem;
        }
        
        .content {
            padding: 2rem;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin: 2rem 0;
        }
        
        .stat {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 1.5rem;
            text-align: center;
            border-left: 4px solid #3498db;
        }
        
        .stat-number {
            font-size: 2rem;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 0.5rem;
        }
        
        .stat-label {
            color: #7f8c8d;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .legend {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 8px;
            margin: 2rem 0;
            border: 1px solid #e9ecef;
        }
        
        .legend h3 {
            margin: 0 0 1rem 0;
            color: #2c3e50;
        }
        
        .legend-items {
            display: flex;
            flex-wrap: wrap;
            gap: 1.5rem;
        }
        
        .legend-item {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .legend-color {
            width: 20px;
            height: 20px;
            border-radius: 3px;
            border: 1px solid #ddd;
        }
        
        .file-section {
            margin: 2rem 0;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            overflow: hidden;
            background: white;
        }
        
        .file-header {
            background: #2c3e50;
            color: white;
            padding: 1rem 1.5rem;
            font-weight: 600;
            font-size: 1.1rem;
        }
        
        .function-section {
            margin: 1rem 0;
            border: 1px solid #e9ecef;
            border-radius: 6px;
            overflow: hidden;
        }
        
        .function-header {
            background: #34495e;
            color: white;
            padding: 0.8rem 1rem;
            font-weight: 500;
            font-size: 1rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .function-stats {
            font-size: 0.9rem;
            opacity: 0.9;
        }
        
        .code-block {
            background: white;
            border-radius: 0;
            margin: 0;
            overflow-x: auto;
            font-family: 'Fira Code', 'Monaco', 'Consolas', 'Courier New', monospace;
            font-size: 14px;
            line-height: 1.4;
        }
        
        .code-line {
            display: flex;
            min-height: 20px;
            border-bottom: 1px solid #f1f3f4;
        }
        
        .line-number {
            background: #f8f9fa;
            color: #6c757d;
            padding: 0.25rem 0.75rem;
            border-right: 1px solid #e9ecef;
            text-align: right;
            min-width: 60px;
            user-select: none;
            font-weight: 500;
        }
        
        .line-content {
            padding: 0.25rem 1rem;
            flex: 1;
            white-space: pre;
            overflow-x: auto;
        }
        
        .line-covered {
            background: white;
        }
        
        .line-uncovered {
            background: #ffebee;
            border-left: 3px solid #f44336;
        }
        
        .line-uncovered .line-number {
            background: #ffcdd2;
            color: #d32f2f;
            font-weight: bold;
        }
        
        .syntax-keyword {
            color: #d73a49;
            font-weight: 600;
        }
        
        .syntax-string {
            color: #032f62;
        }
        
        .syntax-comment {
            color: #6a737d;
            font-style: italic;
        }
        
        .syntax-number {
            color: #005cc5;
        }
        
        .syntax-function {
            color: #6f42c1;
            font-weight: 600;
        }
        
        .no-coverage-files {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
            color: #155724;
        }
        
        .footer {
            text-align: center;
            margin-top: 3rem;
            padding: 2rem;
            color: #7f8c8d;
            border-top: 1px solid #ecf0f1;
            background: #f8f9fa;
        }
        
        @media (max-width: 768px) {
            body { padding: 1rem; }
            .header h1 { font-size: 2rem; }
            .stats { grid-template-columns: 1fr; }
            .legend-items { flex-direction: column; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Code Coverage Report</h1>
            <p>Generated on """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
        </div>
        <div class="content">"""


def apply_syntax_highlighting(line_content):
    """Apply syntax highlighting to code lines."""
    if not line_content.strip():
        return line_content
    
    # Escape HTML first
    line_content = html.escape(line_content)
    
    # Keywords
    keywords = ['def', 'class', 'import', 'from', 'if', 'else', 'elif', 'for', 'while', 
                'try', 'except', 'finally', 'with', 'as', 'return', 'yield', 'break', 
                'continue', 'pass', 'raise', 'assert', 'del', 'global', 'nonlocal', 
                'lambda', 'True', 'False', 'None', 'and', 'or', 'not', 'in', 'is']
    
    for keyword in keywords:
        pattern = r'\b' + re.escape(keyword) + r'\b'
        line_content = re.sub(pattern, f'<span class="syntax-keyword">{keyword}</span>', line_content)
    
    # Comments
    line_content = re.sub(r'(#.*$)', r'<span class="syntax-comment">\1</span>', line_content)
    
    # Strings (avoid replacing if already highlighted)
    if 'syntax-comment' not in line_content:
        line_content = re.sub(r'("[^"]*")', r'<span class="syntax-string">\1</span>', line_content)
        line_content = re.sub(r"('[^']*')", r'<span class="syntax-string">\1</span>', line_content)
    
    # Numbers
    if 'syntax-string' not in line_content and 'syntax-comment' not in line_content:
        line_content = re.sub(r'\b(\d+\.?\d*)\b', r'<span class="syntax-number">\1</span>', line_content)
    
    # Function calls
    if 'syntax-string' not in line_content and 'syntax-comment' not in line_content:
        line_content = re.sub(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*(?=\()', 
                             r'<span class="syntax-function">\1</span>', line_content)
    
    return line_content


def find_functions_and_classes(source_lines):
    """Find all functions and classes with their start and end lines using AST."""
    try:
        source_code = ''.join(source_lines)
        tree = ast.parse(source_code)
        
        functions = []
        
        class FunctionVisitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                end_line = node.end_lineno if hasattr(node, 'end_lineno') else self._find_end_line(node)
                functions.append({
                    'name': node.name,
                    'type': 'function',
                    'start': node.lineno,
                    'end': end_line,
                    'level': 0  # We'll calculate nesting level separately
                })
                self.generic_visit(node)
            
            def visit_AsyncFunctionDef(self, node):
                end_line = node.end_lineno if hasattr(node, 'end_lineno') else self._find_end_line(node)
                functions.append({
                    'name': f"async {node.name}",
                    'type': 'function',
                    'start': node.lineno,
                    'end': end_line,
                    'level': 0
                })
                self.generic_visit(node)
            
            def visit_ClassDef(self, node):
                end_line = node.end_lineno if hasattr(node, 'end_lineno') else self._find_end_line(node)
                functions.append({
                    'name': node.name,
                    'type': 'class',
                    'start': node.lineno,
                    'end': end_line,
                    'level': 0
                })
                self.generic_visit(node)
            
            def _find_end_line(self, node):
                """Fallback method to find end line for older Python versions."""
                max_line = node.lineno
                for child in ast.walk(node):
                    if hasattr(child, 'lineno') and child.lineno > max_line:
                        max_line = child.lineno
                return min(max_line + 5, len(source_lines))  # Add some buffer
        
        visitor = FunctionVisitor()
        visitor.visit(tree)
        
        return sorted(functions, key=lambda x: x['start'])
        
    except SyntaxError:
        # Fallback to regex-based parsing for files with syntax errors
        return find_functions_regex(source_lines)


def find_functions_regex(source_lines):
    """Fallback function finder using regex."""
    functions = []
    func_stack = []
    
    for i, line in enumerate(source_lines, 1):
        # Detect function/class definition
        func_match = re.match(r'^(\s*)(def|class|async def)\s+(\w+)', line)
        if func_match:
            indent = len(func_match.group(1))
            func_type = 'class' if func_match.group(2) == 'class' else 'function'
            func_name = func_match.group(3)
            if func_match.group(2) == 'async def':
                func_name = f"async {func_name}"
            
            # Close previous functions at same or higher indentation
            while func_stack and func_stack[-1]['indent'] >= indent:
                prev_func = func_stack.pop()
                functions.append({
                    'name': prev_func['name'],
                    'type': prev_func['type'],
                    'start': prev_func['start'],
                    'end': i - 1,
                    'level': len(func_stack)
                })
            
            func_stack.append({
                'name': func_name,
                'type': func_type,
                'start': i,
                'indent': indent
            })
    
    # Close remaining functions
    while func_stack:
        func = func_stack.pop()
        functions.append({
            'name': func['name'],
            'type': func['type'],
            'start': func['start'],
            'end': len(source_lines),
            'level': len(func_stack)
        })
    
    return sorted(functions, key=lambda x: x['start'])


def generate_html_footer():
    """Generate HTML footer."""
    return """
        </div>
        <div class="footer">
            <p>Generated by Enhanced Coverage Report System</p>
        </div>
    </div>
</body>
</html>"""


def generate_detailed_coverage_report():
    """Generate a detailed coverage report with improved styling and function grouping."""
    
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
            analysis[filename] = result
        except Exception as e:
            print(f"Warning: Could not analyze {filename}: {e}")
            continue
    
    # Start building HTML
    html_content = [generate_html_header()]
    
    # Overall stats
    total_statements = sum(len(stmts) for _, stmts, _, missing, _ in analysis.values())
    total_missing = sum(len(missing) for _, _, _, missing, _ in analysis.values())
    total_coverage = ((total_statements - total_missing) / total_statements * 100) if total_statements > 0 else 0
    files_with_issues = len([f for f, (_, _, _, missing, _) in analysis.items() if missing])
    
    html_content.append('<div class="stats">')
    html_content.append(f'''
    <div class="stat">
        <div class="stat-number">{total_coverage:.1f}%</div>
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
    html_content.append('<h3>📖 Legend</h3>')
    html_content.append('<div class="legend-items">')
    html_content.append('<div class="legend-item">')
    html_content.append('<div class="legend-color" style="background-color: white; border: 2px solid #ddd;"></div>')
    html_content.append('<span><strong>Covered lines:</strong> Code executed during testing</span>')
    html_content.append('</div>')
    html_content.append('<div class="legend-item">')
    html_content.append('<div class="legend-color" style="background-color: #ffebee; border: 2px solid #f44336;"></div>')
    html_content.append('<span><strong>Uncovered lines:</strong> Code not executed during testing</span>')
    html_content.append('</div>')
    html_content.append('</div>')
    html_content.append('</div>')
    
    # Files with no coverage issues
    files_with_perfect_coverage = []
    
    # Process each file
    has_issues = False
    for filename, (_, statements, excluded, missing, missing_branches) in analysis.items():
        if not missing:
            files_with_perfect_coverage.append(filename)
            continue
            
        has_issues = True
        file_coverage = ((len(statements) - len(missing)) / len(statements) * 100) if statements else 0
        covered_count = len(statements) - len(missing)
        
        html_content.append('<div class="file-section">')
        html_content.append('<div class="file-header">')
        html_content.append(f'📄 {filename} — {file_coverage:.1f}% coverage ({covered_count}/{len(statements)} lines)')
        html_content.append('</div>')
        
        # Read the source file
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                source_lines = f.readlines()
        except Exception as e:
            html_content.append(f'<p><em>❌ Unable to read source file: {filename} - {e}</em></p>')
            html_content.append('</div>')
            continue
        
        # Find functions and classes
        functions = find_functions_and_classes(source_lines)
        
        # Group missing lines by function/class
        functions_with_issues = []
        missing_set = set(missing)
        
        for func in functions:
            func_lines = set(range(func['start'], func['end'] + 1))
            missed_in_func = sorted(missing_set & func_lines)
            if missed_in_func:
                func_coverage = ((len(func_lines) - len(missed_in_func)) / len(func_lines) * 100) if func_lines else 0
                functions_with_issues.append({
                    **func,
                    'missing_lines': missed_in_func,
                    'coverage': func_coverage,
                    'total_lines': len(func_lines)
                })
        
        # Display functions with coverage issues
        for func in functions_with_issues:
            missing_count = len(func['missing_lines'])
            icon = "🏛️" if func['type'] == 'class' else "⚙️"
            
            html_content.append('<div class="function-section">')
            html_content.append('<div class="function-header">')
            html_content.append(f'<span>{icon} {func["type"].title()}: {func["name"]}</span>')
            html_content.append(f'<span class="function-stats">{func["coverage"]:.1f}% coverage, {missing_count} uncovered lines</span>')
            html_content.append('</div>')
            
            html_content.append('<div class="code-block">')
            
            # Show the complete function
            for line_num in range(func['start'], func['end'] + 1):
                if line_num <= len(source_lines):
                    line_content = source_lines[line_num - 1].rstrip()
                    highlighted_content = apply_syntax_highlighting(line_content)
                    
                    is_uncovered = line_num in func['missing_lines']
                    line_class = 'line-uncovered' if is_uncovered else 'line-covered'
                    
                    html_content.append(f'<div class="code-line {line_class}">')
                    html_content.append(f'<div class="line-number">{line_num}</div>')
                    html_content.append(f'<div class="line-content">{highlighted_content}</div>')
                    html_content.append('</div>')
            
            html_content.append('</div>')
            html_content.append('</div>')
        
        html_content.append('</div>')
    
    # Show files with perfect coverage
    if files_with_perfect_coverage:
        html_content.append('<div class="no-coverage-files">')
        html_content.append('<h3>✅ Files with 100% Coverage</h3>')
        html_content.append('<ul>')
        for filename in sorted(files_with_perfect_coverage):
            html_content.append(f'<li>{filename}</li>')
        html_content.append('</ul>')
        html_content.append('</div>')
    
    if not has_issues:
        html_content.append('<div class="no-coverage-files">')
        html_content.append('<h2>🎉 Congratulations!</h2>')
        html_content.append('<p>All measured files have 100% code coverage!</p>')
        html_content.append('</div>')
    
    # Footer
    html_content.append(generate_html_footer())
    
    # Write the report
    output_file = 'tests/reports/coverage.html'
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(html_content))
    
    print(f'✅ Enhanced coverage report generated: {output_file}')
    return True


if __name__ == '__main__':
    success = generate_detailed_coverage_report()
    sys.exit(0 if success else 1)