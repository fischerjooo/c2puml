#!/usr/bin/env python3
"""
Generate detailed per-file coverage reports in HTML format with syntax highlighting.
This script creates beautiful, interactive HTML reports showing line-by-line coverage.
"""

import os
import sys
import subprocess
import json
import html
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import argparse
from datetime import datetime


def print_header(text: str) -> None:
    """Print a header with formatting."""
    print(f"\n{'=' * 60}")
    print(f"  {text}")
    print(f"{'=' * 60}\n")


def print_subheader(text: str) -> None:
    """Print a subheader with formatting."""
    print(f"\n{'-' * 40}")
    print(f"  {text}")
    print(f"{'-' * 40}\n")


def print_success(text: str) -> None:
    """Print success message."""
    print(f"✅ {text}")


def print_error(text: str) -> None:
    """Print error message."""
    print(f"❌ {text}")


def print_info(text: str) -> None:
    """Print info message."""
    print(f"ℹ️  {text}")


def get_coverage_data() -> Optional[Dict]:
    """Get coverage data in JSON format."""
    print_info("Generating coverage JSON data...")
    
    result = subprocess.run(
        ["coverage", "json", "-o", "-"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print_error("Failed to generate coverage JSON")
        return None
    
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print_error("Failed to parse coverage JSON")
        return None


def generate_html_file_report(
    filename: str,
    source_path: Path,
    coverage_info: Dict,
    output_dir: Path
) -> Optional[str]:
    """Generate detailed HTML coverage report for a single file."""
    print_info(f"Generating HTML report for: {filename}")
    
    # Read source file
    try:
        with open(source_path, 'r', encoding='utf-8') as f:
            source_lines = f.readlines()
    except Exception as e:
        print_error(f"Failed to read {filename}: {e}")
        return None
    
    # Get coverage data
    covered_lines = coverage_info.get("executed_lines", [])
    missing_lines = coverage_info.get("missing_lines", [])
    excluded_lines = coverage_info.get("excluded_lines", [])
    
    # Calculate statistics
    total_statements = len(covered_lines) + len(missing_lines)
    coverage_percent = (len(covered_lines) / total_statements * 100) if total_statements > 0 else 100.0
    
    # Create output filename
    safe_filename = filename.replace('/', '_').replace('\\', '_')
    output_file = output_dir / f"{safe_filename}.html"
    
    # Generate HTML
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"""<!DOCTYPE html>
<html>
<head>
    <title>Coverage Report: {html.escape(filename)}</title>
    <style>
        body {{
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }}
        .header {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        h1 {{
            margin: 0 0 10px 0;
            color: #333;
            font-size: 24px;
        }}
        .stats {{
            display: flex;
            gap: 30px;
            margin-top: 20px;
        }}
        .stat {{
            display: flex;
            flex-direction: column;
        }}
        .stat-label {{
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
        }}
        .stat-value {{
            font-size: 24px;
            font-weight: bold;
            color: #333;
        }}
        .coverage-bar {{
            width: 200px;
            height: 20px;
            background: #e0e0e0;
            border-radius: 10px;
            overflow: hidden;
            margin-top: 5px;
        }}
        .coverage-fill {{
            height: 100%;
            background: {'#4caf50' if coverage_percent >= 80 else '#ff9800' if coverage_percent >= 60 else '#f44336'};
            transition: width 0.3s ease;
        }}
        .code-container {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .code-header {{
            background: #333;
            color: white;
            padding: 10px 20px;
            font-size: 14px;
        }}
        .code-lines {{
            display: table;
            width: 100%;
        }}
        .code-line {{
            display: table-row;
            transition: background-color 0.2s;
        }}
        .code-line:hover {{
            background-color: #f0f0f0;
        }}
        .line-number {{
            display: table-cell;
            width: 50px;
            padding: 0 10px;
            text-align: right;
            background: #f8f8f8;
            color: #999;
            border-right: 1px solid #e0e0e0;
            user-select: none;
            font-size: 12px;
            vertical-align: top;
        }}
        .line-status {{
            display: table-cell;
            width: 30px;
            text-align: center;
            font-size: 14px;
            vertical-align: top;
            padding: 0 5px;
        }}
        .line-content {{
            display: table-cell;
            padding: 0 20px;
            white-space: pre;
            font-size: 14px;
            vertical-align: top;
        }}
        .covered {{
            background-color: #e8f5e9;
        }}
        .covered .line-status {{
            color: #4caf50;
        }}
        .missing {{
            background-color: #ffebee;
        }}
        .missing .line-status {{
            color: #f44336;
        }}
        .excluded {{
            background-color: #f5f5f5;
            color: #999;
        }}
        .excluded .line-status {{
            color: #999;
        }}
        .legend {{
            margin-top: 20px;
            padding: 15px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .legend-item {{
            display: inline-block;
            margin-right: 20px;
        }}
        .legend-color {{
            display: inline-block;
            width: 20px;
            height: 20px;
            vertical-align: middle;
            margin-right: 5px;
            border-radius: 3px;
        }}
        .timestamp {{
            color: #666;
            font-size: 12px;
        }}
        /* Syntax highlighting */
        .keyword {{ color: #0000ff; font-weight: bold; }}
        .string {{ color: #008000; }}
        .comment {{ color: #808080; font-style: italic; }}
        .number {{ color: #098658; }}
        .function {{ color: #795E26; }}
        .class {{ color: #267F99; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Coverage Report: {html.escape(filename)}</h1>
        <div class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        
        <div class="stats">
            <div class="stat">
                <span class="stat-label">Coverage</span>
                <span class="stat-value">{coverage_percent:.1f}%</span>
                <div class="coverage-bar">
                    <div class="coverage-fill" style="width: {coverage_percent}%"></div>
                </div>
            </div>
            <div class="stat">
                <span class="stat-label">Statements</span>
                <span class="stat-value">{total_statements}</span>
            </div>
            <div class="stat">
                <span class="stat-label">Covered</span>
                <span class="stat-value" style="color: #4caf50">{len(covered_lines)}</span>
            </div>
            <div class="stat">
                <span class="stat-label">Missing</span>
                <span class="stat-value" style="color: #f44336">{len(missing_lines)}</span>
            </div>
            <div class="stat">
                <span class="stat-label">Excluded</span>
                <span class="stat-value" style="color: #999">{len(excluded_lines)}</span>
            </div>
        </div>
    </div>
    
    <div class="code-container">
        <div class="code-header">Source Code</div>
        <div class="code-lines">
""")
        
        # Generate line-by-line HTML
        for i, line in enumerate(source_lines, 1):
            if i in covered_lines:
                line_class = "covered"
                status_symbol = "✓"
            elif i in missing_lines:
                line_class = "missing"
                status_symbol = "✗"
            elif i in excluded_lines:
                line_class = "excluded"
                status_symbol = "—"
            else:
                line_class = ""
                status_symbol = ""
            
            # Basic syntax highlighting for Python
            highlighted_line = html.escape(line.rstrip('\n'))
            
            # Highlight Python keywords
            python_keywords = ['def', 'class', 'import', 'from', 'if', 'else', 'elif', 
                             'for', 'while', 'try', 'except', 'finally', 'with', 
                             'return', 'yield', 'pass', 'break', 'continue', 'raise',
                             'True', 'False', 'None', 'and', 'or', 'not', 'in', 'is']
            
            for keyword in python_keywords:
                highlighted_line = highlighted_line.replace(
                    f' {keyword} ', f' <span class="keyword">{keyword}</span> '
                ).replace(
                    f'{keyword} ', f'<span class="keyword">{keyword}</span> '
                ).replace(
                    f' {keyword}:', f' <span class="keyword">{keyword}</span>:'
                )
            
            # Highlight strings
            import re
            highlighted_line = re.sub(
                r'(["\'])([^"\']*)\1',
                r'<span class="string">\1\2\1</span>',
                highlighted_line
            )
            
            # Highlight comments
            if '#' in highlighted_line:
                parts = highlighted_line.split('#', 1)
                if len(parts) == 2:
                    highlighted_line = parts[0] + '<span class="comment">#' + parts[1] + '</span>'
            
            f.write(f"""            <div class="code-line {line_class}">
                <div class="line-number">{i}</div>
                <div class="line-status">{status_symbol}</div>
                <div class="line-content">{highlighted_line}</div>
            </div>
""")
        
        f.write("""        </div>
    </div>
    
    <div class="legend">
        <h3 style="margin-top: 0;">Legend</h3>
        <div class="legend-item">
            <span class="legend-color" style="background: #e8f5e9;"></span>
            <span>✓ Covered</span>
        </div>
        <div class="legend-item">
            <span class="legend-color" style="background: #ffebee;"></span>
            <span>✗ Not Covered</span>
        </div>
        <div class="legend-item">
            <span class="legend-color" style="background: #f5f5f5;"></span>
            <span>— Excluded</span>
        </div>
    </div>
</body>
</html>
""")
    
    print_success(f"HTML report generated: {output_file}")
    return safe_filename


def generate_index_html(output_dir: Path, file_reports: List[Tuple[str, float, Dict]]) -> None:
    """Generate an index HTML file with links to all file reports."""
    print_info("Generating HTML index...")
    
    index_file = output_dir / "index.html"
    
    # Sort files by coverage percentage (ascending) so worst coverage is at top
    file_reports.sort(key=lambda x: x[1])
    
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write("""<!DOCTYPE html>
<html>
<head>
    <title>Detailed Coverage Reports</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        h1 {
            color: #333;
            margin-bottom: 10px;
        }
        .timestamp {
            color: #666;
            font-size: 14px;
            margin-bottom: 30px;
        }
        .summary-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .stat-card {
            text-align: center;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        .stat-value {
            font-size: 32px;
            font-weight: bold;
            color: #333;
        }
        .stat-label {
            font-size: 14px;
            color: #666;
            margin-top: 5px;
        }
        .file-list {
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .file-header {
            background: #333;
            color: white;
            padding: 15px 20px;
            font-weight: bold;
        }
        .file-item {
            display: flex;
            align-items: center;
            padding: 15px 20px;
            border-bottom: 1px solid #e0e0e0;
            transition: background-color 0.2s;
        }
        .file-item:hover {
            background-color: #f8f9fa;
        }
        .file-item:last-child {
            border-bottom: none;
        }
        .file-name {
            flex: 1;
            margin-right: 20px;
        }
        .file-name a {
            color: #0066cc;
            text-decoration: none;
        }
        .file-name a:hover {
            text-decoration: underline;
        }
        .file-coverage {
            width: 100px;
            text-align: right;
            font-weight: bold;
        }
        .coverage-bar {
            width: 150px;
            height: 20px;
            background: #e0e0e0;
            border-radius: 10px;
            overflow: hidden;
            margin-left: 20px;
        }
        .coverage-fill {
            height: 100%;
            transition: width 0.3s ease;
        }
        .coverage-high { background: #4caf50; }
        .coverage-medium { background: #ff9800; }
        .coverage-low { background: #f44336; }
        .filter-buttons {
            margin-bottom: 20px;
        }
        .filter-btn {
            padding: 8px 16px;
            margin-right: 10px;
            background: white;
            border: 1px solid #ddd;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .filter-btn:hover {
            background: #f0f0f0;
        }
        .filter-btn.active {
            background: #0066cc;
            color: white;
            border-color: #0066cc;
        }
    </style>
    <script>
        function filterFiles(minCoverage, maxCoverage) {
            const items = document.querySelectorAll('.file-item');
            items.forEach(item => {
                const coverage = parseFloat(item.dataset.coverage);
                if (coverage >= minCoverage && coverage <= maxCoverage) {
                    item.style.display = 'flex';
                } else {
                    item.style.display = 'none';
                }
            });
            
            // Update active button
            document.querySelectorAll('.filter-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            event.target.classList.add('active');
        }
    </script>
</head>
<body>
    <div class="container">
        <h1>Detailed Coverage Reports</h1>
        <div class="timestamp">Generated: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</div>
        
        <div class="summary-card">
            <h2 style="margin-top: 0;">Overall Summary</h2>
            <div class="stats-grid">
""")
        
        # Calculate overall statistics
        total_files = len(file_reports)
        total_covered = sum(stats['covered'] for _, _, stats in file_reports)
        total_missing = sum(stats['missing'] for _, _, stats in file_reports)
        total_statements = total_covered + total_missing
        overall_coverage = (total_covered / total_statements * 100) if total_statements > 0 else 100.0
        
        f.write(f"""                <div class="stat-card">
                    <div class="stat-value">{overall_coverage:.1f}%</div>
                    <div class="stat-label">Overall Coverage</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{total_files}</div>
                    <div class="stat-label">Files Analyzed</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{total_statements:,}</div>
                    <div class="stat-label">Total Statements</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" style="color: #4caf50">{total_covered:,}</div>
                    <div class="stat-label">Covered Lines</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" style="color: #f44336">{total_missing:,}</div>
                    <div class="stat-label">Missing Lines</div>
                </div>
            </div>
        </div>
        
        <div class="filter-buttons">
            <button class="filter-btn active" onclick="filterFiles(0, 100)">All Files</button>
            <button class="filter-btn" onclick="filterFiles(0, 60)">Low Coverage (&lt;60%)</button>
            <button class="filter-btn" onclick="filterFiles(60, 80)">Medium Coverage (60-80%)</button>
            <button class="filter-btn" onclick="filterFiles(80, 100)">High Coverage (&gt;80%)</button>
        </div>
        
        <div class="file-list">
            <div class="file-header">File Coverage Reports</div>
""")
        
        for filename, coverage_percent, stats in file_reports:
            safe_filename = filename.replace('/', '_').replace('\\', '_')
            coverage_class = 'coverage-high' if coverage_percent >= 80 else 'coverage-medium' if coverage_percent >= 60 else 'coverage-low'
            
            f.write(f"""            <div class="file-item" data-coverage="{coverage_percent}">
                <div class="file-name">
                    <a href="{safe_filename}.html">{html.escape(filename)}</a>
                </div>
                <div class="file-coverage" style="color: {'#4caf50' if coverage_percent >= 80 else '#ff9800' if coverage_percent >= 60 else '#f44336'}">
                    {coverage_percent:.1f}%
                </div>
                <div class="coverage-bar">
                    <div class="coverage-fill {coverage_class}" style="width: {coverage_percent}%"></div>
                </div>
            </div>
""")
        
        f.write("""        </div>
    </div>
</body>
</html>
""")
    
    print_success(f"HTML index generated: {index_file}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Generate detailed per-file coverage HTML reports"
    )
    parser.add_argument(
        "--output-dir",
        default="tests/reports/detailed-coverage",
        help="Output directory for coverage reports"
    )
    parser.add_argument(
        "--source-dir",
        default="c_to_plantuml",
        help="Source directory to analyze"
    )
    
    args = parser.parse_args()
    
    print_header("Detailed HTML Coverage Report Generator")
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Get coverage data
    coverage_data = get_coverage_data()
    if not coverage_data:
        print_error("No coverage data available. Run tests with coverage first.")
        return 1
    
    # Process each file
    files_data = coverage_data.get("files", {})
    if not files_data:
        print_error("No files found in coverage data")
        return 1
    
    print_subheader(f"Processing {len(files_data)} files")
    
    file_reports = []
    
    for filename, file_coverage in files_data.items():
        # Skip non-source files
        if not filename.startswith(args.source_dir):
            continue
        
        source_path = Path(filename)
        if not source_path.exists():
            print_error(f"Source file not found: {filename}")
            continue
        
        safe_filename = generate_html_file_report(
            filename,
            source_path,
            file_coverage,
            output_dir
        )
        
        if safe_filename:
            # Calculate coverage percentage for this file
            covered = len(file_coverage.get("executed_lines", []))
            missing = len(file_coverage.get("missing_lines", []))
            total = covered + missing
            coverage_percent = (covered / total * 100) if total > 0 else 100.0
            
            file_reports.append((
                filename,
                coverage_percent,
                {'covered': covered, 'missing': missing}
            ))
    
    # Generate index HTML
    if file_reports:
        generate_index_html(output_dir, file_reports)
    
    print_header("HTML Coverage Report Generation Complete!")
    print_info(f"Reports available in: {output_dir}")
    print_info(f"Open {output_dir}/index.html in your browser")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())