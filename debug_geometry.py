#!/usr/bin/env python3

import json
from pathlib import Path
from c_to_plantuml.models import ProjectModel
from c_to_plantuml.generator import PlantUMLGenerator

def debug_geometry_include_tree():
    # Load the model
    with open('output/model_transformed.json', 'r') as f:
        model_data = json.load(f)
    
    project_model = ProjectModel.from_dict(model_data)
    
    # Find geometry.c
    geometry_c = None
    for file_path, file_model in project_model.files.items():
        if file_path.endswith('geometry.c'):
            geometry_c = file_model
            break
    
    if not geometry_c:
        print("❌ geometry.c not found in model")
        return
    
    print(f"✅ Found geometry.c: {geometry_c.file_path}")
    print(f"   Includes: {geometry_c.includes}")
    
    # Debug _find_include_file method
    generator = PlantUMLGenerator()
    print(f"\n🔍 Debugging _find_include_file:")
    
    # Check what files are in the model
    print(f"📁 Files in model:")
    for file_path in project_model.files.keys():
        print(f"   {file_path}")
    
    # Test finding logger.h
    print(f"\n🔍 Testing _find_include_file for 'logger.h':")
    result = generator._find_include_file('logger.h', project_model)
    print(f"   Result: {result}")
    
    # Test finding other includes
    for include in ['sample.h', 'math_utils.h', 'config.h']:
        result = generator._find_include_file(include, project_model)
        print(f"   {include}: {result}")
    
    # Debug include tree building with depth=3
    print(f"\n🔍 Debugging include tree building (depth=3):")
    include_tree = {}
    visited = set()
    
    def add_file_to_tree(file_path: str, depth: int):
        print(f"   Trying to add {file_path} at depth {depth}")
        if depth > 3 or file_path in visited:
            print(f"     Skipping {file_path} (depth={depth}, visited={file_path in visited})")
            return
        
        visited.add(file_path)
        if file_path in project_model.files:
            include_tree[file_path] = project_model.files[file_path]
            print(f"     ✅ Added {file_path} to tree")
            
            # Add included files
            if depth < 3:
                for include in project_model.files[file_path].includes:
                    print(f"       Processing include: {include}")
                    # Find the actual file path for this include
                    include_path = generator._find_include_file(include, project_model)
                    if include_path:
                        print(f"         Found include path: {include_path}")
                        add_file_to_tree(include_path, depth + 1)
                    else:
                        print(f"         ❌ Could not find include path for {include}")
        else:
            print(f"     ❌ {file_path} not found in project_model.files")
    
    # Start with the root file
    root_key = Path(geometry_c.file_path).name
    print(f"   Starting with root key: {root_key}")
    add_file_to_tree(root_key, 0)
    
    print(f"\n📁 Final include tree:")
    for file_path, file_model in include_tree.items():
        print(f"   {file_path}:")
        print(f"     - Includes: {file_model.includes}")
        print(f"     - Structs: {list(file_model.structs.keys())}")
        print(f"     - Enums: {list(file_model.enums.keys())}")
        print(f"     - Aliases: {list(file_model.aliases.keys())}")
        print(f"     - Unions: {list(file_model.unions.keys())}")
    
    # Check if log_level_t is in any of the files
    print(f"\n🔍 Looking for log_level_t:")
    found_log_level = False
    for file_path, file_model in include_tree.items():
        if 'log_level_t' in file_model.enums:
            print(f"   ✅ Found log_level_t in {file_path}")
            found_log_level = True
            enum_data = file_model.enums['log_level_t']
            print(f"      Values: {[v.name for v in enum_data.values]}")
    
    if not found_log_level:
        print("   ❌ log_level_t not found in include tree")
        
        # Check if logger.h is in the model
        logger_h = None
        for file_path, file_model in project_model.files.items():
            if file_path.endswith('logger.h'):
                logger_h = file_model
                break
        
        if logger_h:
            print(f"   📄 logger.h exists in model:")
            print(f"      - Includes: {logger_h.includes}")
            print(f"      - Enums: {list(logger_h.enums.keys())}")
            if 'log_level_t' in logger_h.enums:
                print(f"      - ✅ log_level_t found in logger.h")
            else:
                print(f"      - ❌ log_level_t not found in logger.h")
        else:
            print("   ❌ logger.h not found in model")

if __name__ == "__main__":
    debug_geometry_include_tree()