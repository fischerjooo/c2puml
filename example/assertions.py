#!/usr/bin/env python3
"""
Comprehensive assertions for validating generated PUML files against expected output.
This script validates that the generator produces the correct PlantUML diagrams.
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple


class PUMLValidator:
    """Validates generated PUML files against expected content."""
    
    def __init__(self, output_dir: str = "../output"):
        self.output_dir = Path(output_dir)
        self.expected_files = [
            "typedef_test.puml",
            "geometry.puml", 
            "logger.puml",
            "math_utils.puml",
            "sample.puml"
        ]
        
    def assert_file_exists(self, filename: str) -> None:
        """Assert that a PUML file exists."""
        filepath = self.output_dir / filename
        assert filepath.exists(), f"File {filename} does not exist at {filepath}"
        print(f"✅ {filename} exists")
        
    def read_puml_file(self, filename: str) -> str:
        """Read and return the content of a PUML file."""
        filepath = self.output_dir / filename
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
            
    def extract_classes(self, content: str) -> Dict[str, Dict]:
        """Extract all class definitions from PUML content."""
        classes = {}
        class_pattern = r'class\s+"([^"]+)"\s+as\s+(\w+)\s+<<(\w+)>>\s+#(\w+)\s*\n\s*\{([^}]+)\}'
        matches = re.finditer(class_pattern, content, re.DOTALL)
        
        for match in matches:
            class_name = match.group(1)
            uml_id = match.group(2)
            stereotype = match.group(3)
            color = match.group(4)
            body = match.group(5).strip()
            
            classes[uml_id] = {
                'name': class_name,
                'stereotype': stereotype,
                'color': color,
                'body': body
            }
            
        return classes
        
    def extract_relationships(self, content: str) -> List[Tuple[str, str, str]]:
        """Extract all relationships from PUML content."""
        relationships = []
        # Include relationships: A --> B : <<include>>
        include_pattern = r'(\w+)\s+-->\s+(\w+)\s+:\s+<<include>>'
        includes = re.findall(include_pattern, content)
        for source, target in includes:
            relationships.append((source, target, 'include'))
            
        # Declaration relationships: A ..> B : <<declares>>
        declare_pattern = r'(\w+)\s+\.\.>\s+(\w+)\s+:\s+<<declares>>'
        declares = re.findall(declare_pattern, content)
        for source, target in declares:
            relationships.append((source, target, 'declares'))
            
        # Uses relationships: A ..> B : <<uses>>
        uses_pattern = r'(\w+)\s+\.\.>\s+(\w+)\s+:\s+<<uses>>'
        uses = re.findall(uses_pattern, content)
        for source, target in uses:
            relationships.append((source, target, 'uses'))
            
        return relationships
        
    def assert_class_structure(self, classes: Dict[str, Dict], filename: str) -> None:
        """Assert that classes have the correct structure and content."""
        print(f"\n🔍 Validating class structure for {filename}:")
        
        for uml_id, class_info in classes.items():
            print(f"  📋 Class: {class_info['name']} ({uml_id})")
            
            # Assert stereotype
            assert class_info['stereotype'] in ['source', 'header', 'typedef'], \
                f"Invalid stereotype '{class_info['stereotype']}' for class {uml_id}"
                
            # Assert color
            assert class_info['color'] in ['LightBlue', 'LightGreen', 'LightYellow', 'LightGray'], \
                f"Invalid color '{class_info['color']}' for class {uml_id}"
                
            # Assert UML_ID naming convention
            if class_info['stereotype'] == 'source':
                # Source files should be named after the filename in uppercase
                expected_name = class_info['name'].upper().replace('-', '_').replace('.', '_')
                assert uml_id == expected_name, \
                    f"Source class {uml_id} should be named {expected_name} (filename in uppercase)"
            elif class_info['stereotype'] == 'header':
                assert uml_id.startswith('HEADER_'), \
                    f"Header class {uml_id} should have HEADER_ prefix"
            elif class_info['stereotype'] == 'typedef':
                assert uml_id.startswith('TYPEDEF_'), \
                    f"Typedef class {uml_id} should have TYPEDEF_ prefix"
                    
            print(f"    ✅ Structure valid")
            
    def assert_class_content(self, classes: Dict[str, Dict], filename: str) -> None:
        """Assert that class content matches expected patterns."""
        print(f"\n📝 Validating class content for {filename}:")
        
        for uml_id, class_info in classes.items():
            body = class_info['body']
            stereotype = class_info['stereotype']
            
            print(f"  📋 Content validation for {uml_id}:")
            
            if stereotype == 'source':
                # Source files should not have + prefix for global variables and functions
                assert not re.search(r'^\s*\+\s+[a-zA-Z_][a-zA-Z0-9_]*\s+[a-zA-Z_][a-zA-Z0-9_]*$', body, re.MULTILINE), \
                    f"Source class {uml_id} should not have + prefix for global variables"
                assert not re.search(r'^\s*\+\s+[a-zA-Z_][a-zA-Z0-9_]*\s+[a-zA-Z_][a-zA-Z0-9_]*\(', body, re.MULTILINE), \
                    f"Source class {uml_id} should not have + prefix for functions"
                    
            elif stereotype == 'header':
                # Header files should have + prefix for all elements
                lines = body.strip().split('\n')
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith("'") and not line.startswith("--"):
                        if not line.startswith('+') and not line.startswith('--'):
                            print(f"    ⚠️  Warning: Header line '{line}' might not have + prefix")
                            
            elif stereotype == 'typedef':
                # Typedef classes should have + prefix for all elements
                lines = body.strip().split('\n')
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith("'") and not line.startswith("--"):
                        if not line.startswith('+'):
                            print(f"    ⚠️  Warning: Typedef line '{line}' might not have + prefix")
                            
            print(f"    ✅ Content patterns valid")
            
    def assert_relationships(self, relationships: List[Tuple[str, str, str]], filename: str) -> None:
        """Assert that relationships are properly structured."""
        print(f"\n🔗 Validating relationships for {filename}:")
        
        # Group relationships by type
        includes = [(s, t) for s, t, r in relationships if r == 'include']
        declares = [(s, t) for s, t, r in relationships if r == 'declares']
        uses = [(s, t) for s, t, r in relationships if r == 'uses']
        
        print(f"  📊 Relationship counts:")
        print(f"    Include: {len(includes)}")
        print(f"    Declares: {len(declares)}")
        print(f"    Uses: {len(uses)}")
        
        # Assert relationship structure
        for source, target, rel_type in relationships:
            assert source and target, f"Invalid relationship: {source} -> {target}"
            assert rel_type in ['include', 'declares', 'uses'], f"Invalid relationship type: {rel_type}"
            
        print(f"    ✅ Relationship structure valid")
        
    def assert_specific_content(self, content: str, filename: str) -> None:
        """Assert specific content requirements for each file."""
        print(f"\n🎯 Validating specific content for {filename}:")
        
        if filename == "typedef_test.puml":
            # Should have specific typedef classes
            assert 'TYPEDEF_MYLEN' in content, "Missing TYPEDEF_MYLEN class"
            assert 'TYPEDEF_MYINT' in content, "Missing TYPEDEF_MYINT class"
            assert 'TYPEDEF_MYSTRING' in content, "Missing TYPEDEF_MYSTRING class"
            assert 'TYPEDEF_MYBUFFER' in content, "Missing TYPEDEF_MYBUFFER class"
            assert 'TYPEDEF_MYCALLBACK' in content, "Missing TYPEDEF_MYCALLBACK class"
            assert 'TYPEDEF_MYCOMPLEX' in content, "Missing TYPEDEF_MYCOMPLEX class"
            assert 'TYPEDEF_MYCOMPLEXPTR' in content, "Missing TYPEDEF_MYCOMPLEXPTR class"
            assert 'TYPEDEF_COLOR_T' in content, "Missing TYPEDEF_COLOR_T class"
            assert 'TYPEDEF_STATUS_T' in content, "Missing TYPEDEF_STATUS_T class"
            assert 'TYPEDEF_POINT_T' in content, "Missing TYPEDEF_POINT_T class"
            assert 'TYPEDEF_POINT_T_2' in content, "Missing TYPEDEF_POINT_T_2 class"
            assert 'TYPEDEF_NAMEDSTRUCT_T' in content, "Missing TYPEDEF_NAMEDSTRUCT_T class"
            assert 'TYPEDEF_NUMBER_T' in content, "Missing TYPEDEF_NUMBER_T class"
            assert 'TYPEDEF_NAMEDUNION_T' in content, "Missing TYPEDEF_NAMEDUNION_T class"
            assert 'TYPEDEF_MYCOMPLEXARRAY' in content, "Missing TYPEDEF_MYCOMPLEXARRAY class"
            assert 'TYPEDEF_SYSTEM_STATE_T' in content, "Missing TYPEDEF_SYSTEM_STATE_T class"
            assert 'TYPEDEF_TRIANGLE_T' in content, "Missing TYPEDEF_TRIANGLE_T class"
            assert 'TYPEDEF_LOG_LEVEL_T' in content, "Missing TYPEDEF_LOG_LEVEL_T class"
            assert 'TYPEDEF_LOGCALLBACK_T' in content, "Missing TYPEDEF_LOGCALLBACK_T class"
            assert 'TYPEDEF_NESTEDINFO_T' in content, "Missing TYPEDEF_NESTEDINFO_T class"
            assert 'TYPEDEF_CE_STATUS_T' in content, "Missing TYPEDEF_CE_STATUS_T class"
            assert 'TYPEDEF_COMPLEXEXAMPLE_T' in content, "Missing TYPEDEF_COMPLEXEXAMPLE_T class"
            
            # Should have specific relationships
            assert 'TYPEDEF_MYBUFFER ..> TYPEDEF_MYLEN : <<uses>>' in content, "Missing MyBuffer uses MyLen relationship"
            assert 'TYPEDEF_MYBUFFER ..> TYPEDEF_MYSTRING : <<uses>>' in content, "Missing MyBuffer uses MyString relationship"
            assert 'TYPEDEF_MYCALLBACK ..> TYPEDEF_MYBUFFER : <<uses>>' in content, "Missing MyCallback uses MyBuffer relationship"
            assert 'TYPEDEF_MYCOMPLEX ..> TYPEDEF_MYLEN : <<uses>>' in content, "Missing MyComplex uses MyLen relationship"
            assert 'TYPEDEF_MYCOMPLEX ..> TYPEDEF_MYSTRING : <<uses>>' in content, "Missing MyComplex uses MyString relationship"
            assert 'TYPEDEF_MYCOMPLEX ..> TYPEDEF_MYCALLBACK : <<uses>>' in content, "Missing MyComplex uses MyCallback relationship"
            assert 'TYPEDEF_MYCOMPLEX ..> TYPEDEF_LOG_LEVEL_T : <<uses>>' in content, "Missing MyComplex uses log_level_t relationship"
            assert 'TYPEDEF_MYCOMPLEXPTR ..> TYPEDEF_MYCOMPLEX : <<uses>>' in content, "Missing MyComplexPtr uses MyComplex relationship"
            assert 'TYPEDEF_MYCOMPLEXARRAY ..> TYPEDEF_MYCOMPLEXPTR : <<uses>>' in content, "Missing MyComplexArray uses MyComplexPtr relationship"
            assert 'TYPEDEF_TRIANGLE_T ..> TYPEDEF_POINT_T_2 : <<uses>>' in content, "Missing triangle_t uses point_t relationship"
            assert 'TYPEDEF_LOGCALLBACK_T ..> TYPEDEF_LOG_LEVEL_T : <<uses>>' in content, "Missing log_callback_t uses log_level_t relationship"
            assert 'TYPEDEF_NESTEDINFO_T ..> TYPEDEF_LOG_LEVEL_T : <<uses>>' in content, "Missing NestedInfo_t uses log_level_t relationship"
            assert 'TYPEDEF_COMPLEXEXAMPLE_T ..> TYPEDEF_NESTEDINFO_T : <<uses>>' in content, "Missing ComplexExample_t uses NestedInfo_t relationship"
            assert 'TYPEDEF_COMPLEXEXAMPLE_T ..> TYPEDEF_CE_STATUS_T : <<uses>>' in content, "Missing ComplexExample_t uses CE_Status_t relationship"
            
        elif filename == "geometry.puml":
            assert 'TYPEDEF_TRIANGLE_T' in content, "Missing TYPEDEF_TRIANGLE_T class"
            assert 'TYPEDEF_POINT_T' in content, "Missing TYPEDEF_POINT_T class"
            assert 'TYPEDEF_SYSTEM_STATE_T' in content, "Missing TYPEDEF_SYSTEM_STATE_T class"
            assert 'TYPEDEF_LOG_LEVEL_T' in content, "Missing TYPEDEF_LOG_LEVEL_T class"
            assert 'TYPEDEF_TRIANGLE_T ..> TYPEDEF_POINT_T : <<uses>>' in content, "Missing triangle_t uses point_t relationship"
            
        elif filename == "logger.puml":
            assert 'TYPEDEF_LOG_LEVEL_T' in content, "Missing TYPEDEF_LOG_LEVEL_T class"
            assert 'TYPEDEF_LOGCALLBACK_T' in content, "Missing TYPEDEF_LOGCALLBACK_T class"
            assert 'TYPEDEF_LOGCALLBACK_T ..> TYPEDEF_LOG_LEVEL_T : <<uses>>' in content, "Missing log_callback_t uses log_level_t relationship"
            
        elif filename == "sample.puml":
            assert 'TYPEDEF_POINT_T' in content, "Missing TYPEDEF_POINT_T class"
            assert 'TYPEDEF_SYSTEM_STATE_T' in content, "Missing TYPEDEF_SYSTEM_STATE_T class"
            assert 'TYPEDEF_TRIANGLE_T' in content, "Missing TYPEDEF_TRIANGLE_T class"
            assert 'TYPEDEF_LOG_LEVEL_T' in content, "Missing TYPEDEF_LOG_LEVEL_T class"
            assert 'TYPEDEF_TRIANGLE_T ..> TYPEDEF_POINT_T : <<uses>>' in content, "Missing triangle_t uses point_t relationship"
            
        elif filename == "math_utils.puml":
            # math_utils.puml should be simple with no typedefs
            assert 'TYPEDEF_' not in content, "math_utils.puml should not contain typedef classes"
            
        print(f"    ✅ Specific content valid")
        
    def validate_file(self, filename: str) -> None:
        """Validate a single PUML file."""
        print(f"\n{'='*60}")
        print(f"🔍 Validating {filename}")
        print(f"{'='*60}")
        
        # Assert file exists
        self.assert_file_exists(filename)
        
        # Read file content
        content = self.read_puml_file(filename)
        
        # Extract and validate classes
        classes = self.extract_classes(content)
        self.assert_class_structure(classes, filename)
        self.assert_class_content(classes, filename)
        
        # Extract and validate relationships
        relationships = self.extract_relationships(content)
        self.assert_relationships(relationships, filename)
        
        # Validate specific content requirements
        self.assert_specific_content(content, filename)
        
        print(f"\n✅ {filename} validation completed successfully!")
        
    def run_all_validations(self) -> None:
        """Run validation for all expected PUML files."""
        print("🚀 Starting comprehensive PUML file validation...")
        print(f"📁 Output directory: {self.output_dir.absolute()}")
        
        # Check if output directory exists
        assert self.output_dir.exists(), f"Output directory {self.output_dir} does not exist"
        
        # Validate each file
        for filename in self.expected_files:
            try:
                self.validate_file(filename)
            except AssertionError as e:
                print(f"\n❌ Validation failed for {filename}: {e}")
                sys.exit(1)
            except Exception as e:
                print(f"\n💥 Unexpected error validating {filename}: {e}")
                sys.exit(1)
                
        print(f"\n{'='*60}")
        print("🎉 All PUML files validated successfully!")
        print(f"{'='*60}")


def main():
    """Main function to run the validation."""
    validator = PUMLValidator()
    validator.run_all_validations()


if __name__ == "__main__":
    main()