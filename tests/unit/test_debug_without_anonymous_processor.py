import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.c2puml.core.parser import CParser
from pathlib import Path
import tempfile
import re

def test_debug_without_anonymous_processor():
    """Debug what happens without the AnonymousTypedefProcessor"""
    
    # Test code with complex nested union
    test_code = """
    typedef union {
        int primary_int;
        union {
            float nested_float;
            double nested_double;
            union {
                char deep_char;
                short deep_short;
            } deep_union;
        } nested_union;
        char primary_bytes[32];
    } union_with_union_t;
    """
    
    # Create a temporary file with the test code
    with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
        f.write(test_code)
        temp_file = f.name
    
    try:
        # Parse the file
        parser = CParser()
        file_model = parser.parse_file(Path(temp_file), "test.c")
        
        # Check what unions were parsed
        print(f"Available unions: {list(file_model.unions.keys())}")
        
        if "union_with_union_t" in file_model.unions:
            union = file_model.unions["union_with_union_t"]
            print(f"Union fields: {[(f.name, f.type) for f in union.fields]}")
            
            # Debug: Check each field type
            print(f"\n=== FIELD TYPE DEBUG ===")
            for i, field in enumerate(union.fields):
                print(f"Field {i}: name='{field.name}', type='{field.type}'")
                if 'union {' in field.type or 'struct {' in field.type:
                    print(f"  Contains nested structure")
                    if re.search(r'\}\s+\w+\s*$', field.type):
                        print(f"  Ends with field name pattern")
                    else:
                        print(f"  Does NOT end with field name pattern")
            
            # Check what the anonymous union contains
            if "union_with_union_t_anonymous_union_1" in file_model.unions:
                anon_union = file_model.unions["union_with_union_t_anonymous_union_1"]
                print(f"\n=== ANONYMOUS UNION DEBUG ===")
                print(f"Anonymous union fields: {[(f.name, f.type) for f in anon_union.fields]}")
            
            # Check anonymous relationships
            print(f"\n=== ANONYMOUS RELATIONSHIPS ===")
            print(f"Anonymous relationships: {file_model.anonymous_relationships}")
            
            # Check field names
            field_names = [f.name for f in union.fields]
            print(f"\nField names: {field_names}")
            
            # Expected field names
            expected_names = ["primary_int", "nested_union", "primary_bytes"]
            print(f"Expected field names: {expected_names}")
            print(f"Match: {field_names == expected_names}")
        
    finally:
        # Clean up
        Path(temp_file).unlink()

if __name__ == "__main__":
    test_debug_without_anonymous_processor()