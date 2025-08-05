#!/usr/bin/env python3
"""
TODO Recommendations for C2PUML Test Migration

This script analyzes each test file in the current test suite and provides
specific recommendations for migration to the unified testing framework
based on the requirements defined in todo.md.

For each test file, it analyzes:
1. Number of test methods
2. Current testing approach (internal vs external)
3. Input requirements (single vs multiple)
4. Recommended migration strategy
5. Proposed folder structure
6. Data file requirements

Progress tracking is included with status updates.
"""

import os
import re
import ast
import json
from pathlib import Path
from typing import Dict, List, Tuple, NamedTuple
from dataclasses import dataclass, asdict
from enum import Enum


class InputStrategy(Enum):
    """Input strategy for test migration"""
    EXPLICIT_FILES = "explicit_files"  # Single input folder with .c/.h files
    DATA_JSON = "data_json"  # Multiple data_*.json files
    MIXED_SPLIT = "mixed_split"  # Split into multiple test files


class Priority(Enum):
    """Migration priority levels"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class TestMethodAnalysis:
    """Analysis of a single test method"""
    name: str
    line_number: int
    uses_internal_apis: bool
    likely_input_requirements: str
    complexity_score: int


@dataclass
class TestFileAnalysis:
    """Complete analysis of a test file"""
    file_path: str
    category: str  # unit, feature, integration
    test_class_name: str
    test_methods: List[TestMethodAnalysis]
    total_methods: int
    uses_internal_apis: bool
    estimated_input_diversity: str  # "single", "multiple", "mixed"
    file_size_lines: int
    priority: Priority
    recommended_strategy: InputStrategy
    should_split: bool
    split_suggestions: List[str]


@dataclass
class MigrationRecommendation:
    """Migration recommendation for a test file"""
    original_file: str
    analysis: TestFileAnalysis
    recommended_structure: Dict
    data_json_files: List[str]
    explicit_files: List[str]
    migration_notes: List[str]
    estimated_effort: str  # "low", "medium", "high"
    dependencies: List[str]


class TestAnalyzer:
    """Analyzes test files and generates migration recommendations"""
    
    def __init__(self, tests_dir: str = "tests"):
        self.tests_dir = Path(tests_dir)
        self.recommendations: List[MigrationRecommendation] = []
        self.progress_log: List[str] = []
        
    def log_progress(self, message: str):
        """Log progress message"""
        print(f"[ANALYSIS] {message}")
        self.progress_log.append(message)
    
    def analyze_test_file(self, file_path: Path) -> TestFileAnalysis:
        """Analyze a single test file"""
        self.log_progress(f"Analyzing {file_path.name}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Count lines
        file_size_lines = len(content.splitlines())
        
        # Parse AST to find test methods
        try:
            tree = ast.parse(content)
            test_methods = []
            test_class_name = "Unknown"
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and "Test" in node.name:
                    test_class_name = node.name
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef) and item.name.startswith("test_"):
                            method_analysis = self._analyze_test_method(item, content)
                            test_methods.append(method_analysis)
                            
        except SyntaxError:
            self.log_progress(f"WARNING: Could not parse {file_path.name}")
            test_methods = self._fallback_method_detection(content)
            
        # Determine category
        category = self._get_test_category(file_path)
        
        # Analyze internal API usage
        uses_internal_apis = self._detect_internal_api_usage(content)
        
        # Estimate input diversity
        input_diversity = self._estimate_input_diversity(test_methods, content)
        
        # Determine priority based on various factors
        priority = self._calculate_priority(file_path, len(test_methods), uses_internal_apis)
        
        # Recommend strategy
        recommended_strategy = self._recommend_strategy(test_methods, input_diversity, file_size_lines)
        
        # Check if file should be split
        should_split, split_suggestions = self._analyze_split_requirements(test_methods, file_size_lines)
        
        return TestFileAnalysis(
            file_path=str(file_path),
            category=category,
            test_class_name=test_class_name,
            test_methods=test_methods,
            total_methods=len(test_methods),
            uses_internal_apis=uses_internal_apis,
            estimated_input_diversity=input_diversity,
            file_size_lines=file_size_lines,
            priority=priority,
            recommended_strategy=recommended_strategy,
            should_split=should_split,
            split_suggestions=split_suggestions
        )
    
    def _analyze_test_method(self, method_node: ast.FunctionDef, content: str) -> TestMethodAnalysis:
        """Analyze a single test method"""
        method_name = method_node.name
        line_number = method_node.lineno
        
        # Get method source
        lines = content.splitlines()
        method_start = line_number - 1
        method_end = method_start + 20  # Look at first 20 lines of method
        method_source = "\n".join(lines[method_start:min(method_end, len(lines))])
        
        # Check for internal API usage
        uses_internal = any(pattern in method_source for pattern in [
            "from c2puml.core", "from c2puml.parser", "from c2puml.tokenizer",
            "CParser()", "CTokenizer()", "Parser()", "Generator()", "Transformer()"
        ])
        
        # Estimate input requirements based on method name and content
        input_reqs = self._estimate_method_input_requirements(method_name, method_source)
        
        # Calculate complexity score
        complexity = self._calculate_method_complexity(method_source)
        
        return TestMethodAnalysis(
            name=method_name,
            line_number=line_number,
            uses_internal_apis=uses_internal,
            likely_input_requirements=input_reqs,
            complexity_score=complexity
        )
    
    def _fallback_method_detection(self, content: str) -> List[TestMethodAnalysis]:
        """Fallback method to detect test methods using regex"""
        methods = []
        for match in re.finditer(r'def (test_\w+)\(', content):
            method_name = match.group(1)
            line_number = content[:match.start()].count('\n') + 1
            
            methods.append(TestMethodAnalysis(
                name=method_name,
                line_number=line_number,
                uses_internal_apis=True,  # Assume true for safety
                likely_input_requirements="unknown",
                complexity_score=5  # Medium complexity assumption
            ))
        return methods
    
    def _get_test_category(self, file_path: Path) -> str:
        """Determine test category based on file path"""
        if "unit" in str(file_path):
            return "unit"
        elif "feature" in str(file_path):
            return "feature"
        elif "integration" in str(file_path):
            return "integration"
        elif "example" in str(file_path):
            return "example"
        else:
            return "unknown"
    
    def _detect_internal_api_usage(self, content: str) -> bool:
        """Detect if test uses internal APIs"""
        internal_patterns = [
            r"from c2puml\.core",
            r"from c2puml\.parser",
            r"from c2puml\.tokenizer",
            r"from c2puml\.generator",
            r"from c2puml\.transformer",
            r"CParser\(\)",
            r"CTokenizer\(\)",
            r"\.tokenize\(",
            r"\.parse\(",
            r"\.transform\(",
            r"\.generate\("
        ]
        
        return any(re.search(pattern, content) for pattern in internal_patterns)
    
    def _estimate_input_diversity(self, test_methods: List[TestMethodAnalysis], content: str) -> str:
        """Estimate if test methods need different inputs"""
        if len(test_methods) <= 1:
            return "single"
            
        # Look for patterns indicating different input needs
        diverse_patterns = [
            "tempfile",
            "NamedTemporaryFile",
            "different test cases",
            "various scenarios",
            "multiple inputs"
        ]
        
        # Check method names for diversity indicators
        method_themes = set()
        for method in test_methods:
            if "simple" in method.name:
                method_themes.add("simple")
            elif "complex" in method.name:
                method_themes.add("complex")
            elif "nested" in method.name:
                method_themes.add("nested")
            elif "macro" in method.name:
                method_themes.add("macro")
            elif "struct" in method.name:
                method_themes.add("struct")
            elif "enum" in method.name:
                method_themes.add("enum")
            elif "function" in method.name:
                method_themes.add("function")
        
        if len(method_themes) > 2:
            return "multiple"
        elif any(pattern in content for pattern in diverse_patterns):
            return "multiple"
        else:
            return "single"
    
    def _calculate_priority(self, file_path: Path, method_count: int, uses_internal: bool) -> Priority:
        """Calculate migration priority"""
        # High priority factors
        if uses_internal and method_count > 5:
            return Priority.HIGH
        if "parser" in file_path.name or "tokenizer" in file_path.name:
            return Priority.HIGH
        if "core" in str(file_path) or "main" in file_path.name:
            return Priority.HIGH
            
        # Low priority factors
        if "debug" in file_path.name or method_count <= 2:
            return Priority.LOW
            
        return Priority.MEDIUM
    
    def _recommend_strategy(self, test_methods: List[TestMethodAnalysis], 
                          input_diversity: str, file_size: int) -> InputStrategy:
        """Recommend migration strategy"""
        if input_diversity == "multiple" or len(test_methods) > 10:
            return InputStrategy.DATA_JSON
        elif file_size > 1000 or len(test_methods) > 20:
            return InputStrategy.MIXED_SPLIT
        else:
            return InputStrategy.EXPLICIT_FILES
    
    def _analyze_split_requirements(self, test_methods: List[TestMethodAnalysis], 
                                  file_size: int) -> Tuple[bool, List[str]]:
        """Analyze if file should be split"""
        if len(test_methods) > 25 or file_size > 1500:
            # Group methods by theme
            themes = {}
            for method in test_methods:
                theme = self._extract_method_theme(method.name)
                if theme not in themes:
                    themes[theme] = []
                themes[theme].append(method.name)
            
            if len(themes) > 3:
                split_suggestions = [f"test_{theme}.py" for theme in themes.keys()]
                return True, split_suggestions
                
        return False, []
    
    def _extract_method_theme(self, method_name: str) -> str:
        """Extract theme from method name"""
        if "struct" in method_name:
            return "struct_parsing"
        elif "enum" in method_name:
            return "enum_parsing"
        elif "function" in method_name:
            return "function_parsing"
        elif "macro" in method_name:
            return "macro_processing"
        elif "include" in method_name:
            return "include_processing"
        elif "typedef" in method_name:
            return "typedef_processing"
        elif "generator" in method_name or "format" in method_name:
            return "output_generation"
        elif "transform" in method_name:
            return "transformation"
        else:
            return "general"
    
    def _estimate_method_input_requirements(self, method_name: str, method_source: str) -> str:
        """Estimate input requirements for a method"""
        if "simple" in method_name:
            return "small_data_json"
        elif "complex" in method_name or "comprehensive" in method_name:
            return "explicit_files"
        elif "nested" in method_name or "mixed" in method_name:
            return "medium_data_json"
        elif "tempfile" in method_source or "NamedTemporaryFile" in method_source:
            return "generated_small"
        else:
            return "flexible"
    
    def _calculate_method_complexity(self, method_source: str) -> int:
        """Calculate complexity score for method (1-10)"""
        complexity = 1
        
        # Add complexity for various factors
        if method_source.count('\n') > 50:
            complexity += 2
        if "for " in method_source or "while " in method_source:
            complexity += 1
        if method_source.count("assert") > 5:
            complexity += 1
        if "tempfile" in method_source:
            complexity += 1
        if "subprocess" in method_source or "os.system" in method_source:
            complexity += 2
            
        return min(complexity, 10)
    
    def generate_recommendation(self, analysis: TestFileAnalysis) -> MigrationRecommendation:
        """Generate migration recommendation for a test file"""
        
        # Determine folder structure
        if analysis.should_split:
            # Multiple test files
            recommended_structure = {}
            for suggestion in analysis.split_suggestions:
                test_name = suggestion.replace('.py', '')
                recommended_structure[suggestion] = {
                    "test_file": suggestion,
                    "input_folder": f"test_{test_name}/input/",
                    "config_file": f"test_{test_name}/input/config.json",
                    "assertions_file": f"test_{test_name}/assertions.json"
                }
        else:
            # Single test file
            base_name = Path(analysis.file_path).stem
            recommended_structure = {
                "test_file": f"{base_name}.py",
                "input_folder": f"{base_name}/input/",
                "config_file": f"{base_name}/input/config.json",
                "assertions_file": f"{base_name}/assertions.json"
            }
        
        # Determine data files needed
        data_json_files = []
        explicit_files = []
        
        if analysis.recommended_strategy == InputStrategy.DATA_JSON:
            # Generate data file suggestions based on methods
            method_themes = {}
            for method in analysis.test_methods:
                theme = self._extract_method_theme(method.name)
                if theme not in method_themes:
                    method_themes[theme] = []
                method_themes[theme].append(method.name)
            
            for theme, methods in method_themes.items():
                if len(methods) == 1:
                    data_json_files.append(f"data_{methods[0].replace('test_', '')}.json")
                else:
                    data_json_files.append(f"data_{theme}.json")
                    
        elif analysis.recommended_strategy == InputStrategy.EXPLICIT_FILES:
            # Suggest common explicit files
            explicit_files = ["main.c", "types.h", "utils.h"]
            
        # Generate migration notes
        migration_notes = []
        
        if analysis.uses_internal_apis:
            migration_notes.append("CRITICAL: Convert from internal API usage to CLI-only interface")
            
        if analysis.total_methods > 15:
            migration_notes.append("Consider splitting large test file for better maintainability")
            
        if analysis.estimated_input_diversity == "multiple":
            migration_notes.append("Use data_*.json files - methods need different inputs")
            
        if analysis.priority == Priority.HIGH:
            migration_notes.append("HIGH PRIORITY: Core functionality test")
            
        # Estimate effort
        effort_score = 0
        effort_score += analysis.total_methods * 0.5
        effort_score += 2 if analysis.uses_internal_apis else 0
        effort_score += 3 if analysis.should_split else 0
        effort_score += 2 if analysis.recommended_strategy == InputStrategy.DATA_JSON else 0
        
        if effort_score < 5:
            estimated_effort = "low"
        elif effort_score < 15:
            estimated_effort = "medium"
        else:
            estimated_effort = "high"
            
        # Determine dependencies
        dependencies = []
        if "parser" in analysis.file_path:
            dependencies.append("TestDataFactory implementation")
        if "generator" in analysis.file_path:
            dependencies.append("ModelValidator implementation")
        if "cli" in analysis.file_path:
            dependencies.append("TestExecutor implementation")
            
        return MigrationRecommendation(
            original_file=analysis.file_path,
            analysis=analysis,
            recommended_structure=recommended_structure,
            data_json_files=data_json_files,
            explicit_files=explicit_files,
            migration_notes=migration_notes,
            estimated_effort=estimated_effort,
            dependencies=dependencies
        )
    
    def analyze_all_tests(self) -> List[MigrationRecommendation]:
        """Analyze all test files and generate recommendations"""
        self.log_progress("Starting comprehensive test analysis...")
        
        # Find all test files
        test_files = []
        for category in ["unit", "feature", "integration"]:
            category_dir = self.tests_dir / category
            if category_dir.exists():
                test_files.extend(category_dir.glob("test_*.py"))
        
        self.log_progress(f"Found {len(test_files)} test files to analyze")
        
        # Analyze each file
        for test_file in sorted(test_files):
            try:
                analysis = self.analyze_test_file(test_file)
                recommendation = self.generate_recommendation(analysis)
                self.recommendations.append(recommendation)
                
                self.log_progress(f"✅ {test_file.name}: {analysis.total_methods} methods, "
                                f"{analysis.recommended_strategy.value}, "
                                f"{analysis.priority.value} priority")
                                
            except Exception as e:
                self.log_progress(f"❌ Error analyzing {test_file.name}: {e}")
        
        self.log_progress(f"Analysis complete! Generated {len(self.recommendations)} recommendations")
        return self.recommendations
    
    def save_recommendations(self, output_file: str = "todo_recommendations.json"):
        """Save recommendations to JSON file"""
        # Convert to serializable format
        recommendations_data = []
        for rec in self.recommendations:
            # Convert dataclasses to dicts
            rec_dict = {
                "original_file": rec.original_file,
                "analysis": asdict(rec.analysis),
                "recommended_structure": rec.recommended_structure,
                "data_json_files": rec.data_json_files,
                "explicit_files": rec.explicit_files,
                "migration_notes": rec.migration_notes,
                "estimated_effort": rec.estimated_effort,
                "dependencies": rec.dependencies
            }
            
            # Handle enums
            rec_dict["analysis"]["priority"] = rec.analysis.priority.value
            rec_dict["analysis"]["recommended_strategy"] = rec.analysis.recommended_strategy.value
            
            recommendations_data.append(rec_dict)
        
        # Save with progress log
        output_data = {
            "analysis_metadata": {
                "total_files_analyzed": len(self.recommendations),
                "high_priority_count": sum(1 for r in self.recommendations if r.analysis.priority == Priority.HIGH),
                "medium_priority_count": sum(1 for r in self.recommendations if r.analysis.priority == Priority.MEDIUM),
                "low_priority_count": sum(1 for r in self.recommendations if r.analysis.priority == Priority.LOW),
                "data_json_strategy_count": sum(1 for r in self.recommendations if r.analysis.recommended_strategy == InputStrategy.DATA_JSON),
                "explicit_files_strategy_count": sum(1 for r in self.recommendations if r.analysis.recommended_strategy == InputStrategy.EXPLICIT_FILES),
                "split_required_count": sum(1 for r in self.recommendations if r.analysis.should_split),
            },
            "progress_log": self.progress_log,
            "recommendations": recommendations_data
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2)
        
        self.log_progress(f"Recommendations saved to {output_file}")
    
    def print_summary(self):
        """Print analysis summary"""
        print("\n" + "="*80)
        print("MIGRATION RECOMMENDATIONS SUMMARY")
        print("="*80)
        
        high_priority = [r for r in self.recommendations if r.analysis.priority == Priority.HIGH]
        medium_priority = [r for r in self.recommendations if r.analysis.priority == Priority.MEDIUM]
        low_priority = [r for r in self.recommendations if r.analysis.priority == Priority.LOW]
        
        print(f"\n📊 PRIORITY BREAKDOWN:")
        print(f"   🔴 High Priority: {len(high_priority)} files")
        print(f"   🟡 Medium Priority: {len(medium_priority)} files")
        print(f"   🟢 Low Priority: {len(low_priority)} files")
        
        data_json_strategy = [r for r in self.recommendations if r.analysis.recommended_strategy == InputStrategy.DATA_JSON]
        explicit_strategy = [r for r in self.recommendations if r.analysis.recommended_strategy == InputStrategy.EXPLICIT_FILES]
        split_strategy = [r for r in self.recommendations if r.analysis.recommended_strategy == InputStrategy.MIXED_SPLIT]
        
        print(f"\n📁 STRATEGY BREAKDOWN:")
        print(f"   📝 Data JSON Strategy: {len(data_json_strategy)} files")
        print(f"   📄 Explicit Files Strategy: {len(explicit_strategy)} files")
        print(f"   🔄 Split Required: {len(split_strategy)} files")
        
        files_to_split = [r for r in self.recommendations if r.analysis.should_split]
        internal_api_usage = [r for r in self.recommendations if r.analysis.uses_internal_apis]
        
        print(f"\n⚠️  MIGRATION CHALLENGES:")
        print(f"   🔧 Internal API Usage: {len(internal_api_usage)} files")
        print(f"   ✂️  Files to Split: {len(files_to_split)} files")
        
        print(f"\n🎯 TOP PRIORITY MIGRATIONS:")
        for rec in sorted(high_priority, key=lambda x: x.analysis.total_methods, reverse=True)[:5]:
            file_name = Path(rec.original_file).name
            print(f"   • {file_name}: {rec.analysis.total_methods} methods, {rec.analysis.recommended_strategy.value}")
        
        print(f"\n📋 DETAILED RECOMMENDATIONS SAVED TO: todo_recommendations.json")
        print("="*80)


def main():
    """Main analysis function"""
    print("C2PUML Test Migration Analysis")
    print("==============================")
    
    analyzer = TestAnalyzer()
    
    # Run complete analysis
    recommendations = analyzer.analyze_all_tests()
    
    # Save detailed recommendations
    analyzer.save_recommendations()
    
    # Print summary
    analyzer.print_summary()
    
    # Generate quick reference for high priority items
    print("\n🚀 QUICK START RECOMMENDATIONS:")
    print("-" * 50)
    
    high_priority_recs = [r for r in recommendations if r.analysis.priority == Priority.HIGH]
    
    for i, rec in enumerate(high_priority_recs[:10], 1):  # Top 10 high priority
        file_name = Path(rec.original_file).name
        strategy = rec.analysis.recommended_strategy.value
        method_count = rec.analysis.total_methods
        
        print(f"{i:2d}. {file_name}")
        print(f"    Strategy: {strategy}")
        print(f"    Methods: {method_count}")
        print(f"    Effort: {rec.estimated_effort}")
        if rec.migration_notes:
            print(f"    Notes: {rec.migration_notes[0]}")
        print()


if __name__ == "__main__":
    main()