#!/usr/bin/env python3
"""
Debug script to test model loading and generator
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from c_to_plantuml.models import ProjectModel
from c_to_plantuml.generator import PlantUMLGenerator

def test_model_loading():
    """Test if the model loads correctly"""
    try:
        # Load the model
        model = ProjectModel.load("output/model.json")
        print(f"✅ Model loaded successfully with {len(model.files)} files")
        
        # List all files in the model
        print("\n📁 Files in model:")
        for file_path in model.files:
            print(f"  - {file_path}")
        
        # Test accessing a specific file
        math_utils_c = None
        for file_path, file_model in model.files.items():
            if file_path.endswith("math_utils.c"):
                math_utils_c = file_model
                break
        
        if math_utils_c:
            print(f"\n✅ Found math_utils.c with {len(math_utils_c.functions)} functions")
            print(f"  Includes: {list(math_utils_c.includes)}")
            for func in math_utils_c.functions:
                print(f"  - {func.name}: {func.return_type}")
                for param in func.parameters:
                    print(f"    param: {param.type} {param.name}")
        else:
            print("❌ math_utils.c not found")
        
        # Test the generator
        generator = PlantUMLGenerator()
        if math_utils_c:
            try:
                # Test include file finding
                print("\n🔍 Testing include file finding:")
                for include in math_utils_c.includes:
                    found_path = generator._find_include_file(include, model)
                    print(f"  Include '{include}' -> Found: {found_path}")
                
                # Test include tree building
                include_tree = generator._build_include_tree(math_utils_c, model, 2)
                print(f"\n✅ Include tree built with {len(include_tree)} files:")
                for file_path in include_tree:
                    print(f"  - {file_path}")
                
                puml_content = generator.generate_diagram(math_utils_c, model, include_depth=2)
                print("\n✅ Generator worked!")
                print("Generated content:")
                print(puml_content)
            except Exception as e:
                print(f"❌ Generator failed: {e}")
                import traceback
                traceback.print_exc()
        
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_model_loading()