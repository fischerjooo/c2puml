#!/usr/bin/env python3

# Script to carefully remove typedef_relations references from generator.py

with open('c_to_plantuml/generator.py', 'r') as f:
    content = f.read()

# Remove all lines that reference typedef_relations
lines = content.split('\n')
filtered_lines = []

i = 0
while i < len(lines):
    line = lines[i]
    
    # Skip lines that reference typedef_relations
    if 'typedef_relations' in line:
        # Skip this line and any indented lines that follow
        while i < len(lines) and (lines[i].strip() == '' or lines[i].startswith(' ') or lines[i].startswith('\t')):
            i += 1
        continue
    
    # Skip lines that reference typedef_relation in loops
    if 'for typedef_relation in' in line:
        # Skip this line and any indented lines that follow
        while i < len(lines) and (lines[i].strip() == '' or lines[i].startswith(' ') or lines[i].startswith('\t')):
            i += 1
        continue
    
    # Skip lines that reference typedef_relation
    if 'typedef_relation.' in line:
        i += 1
        continue
    
    # Skip lines that reference _process_typedef_relationships
    if '_process_typedef_relationships' in line:
        i += 1
        continue
    
    # Skip lines that reference _process_typedef_uses
    if '_process_typedef_uses' in line:
        i += 1
        continue
    
    # Skip lines that reference _process_file_typedef_uses
    if '_process_file_typedef_uses' in line:
        i += 1
        continue
    
    # Skip lines that reference _process_function_pointer_typedef_uses
    if '_process_function_pointer_typedef_uses' in line:
        i += 1
        continue
    
    # Skip lines that reference _process_pointer_typedef_uses
    if '_process_pointer_typedef_uses' in line:
        i += 1
        continue
    
    # Skip lines that reference _process_array_typedef_uses
    if '_process_array_typedef_uses' in line:
        i += 1
        continue
    
    # Skip lines that reference generate_typedef_uses_relations
    if 'generate_typedef_uses_relations' in line:
        i += 1
        continue
    
    # Skip lines that reference typedef_rel
    if 'typedef_rel' in line:
        i += 1
        continue
    
    # Skip lines that reference typedef in typedef_relations context
    if 'for typedef in' in line and 'typedef_relations' in content[max(0, i-10):i+10]:
        i += 1
        continue
    
    filtered_lines.append(line)
    i += 1

content = '\n'.join(filtered_lines)

with open('c_to_plantuml/generator.py', 'w') as f:
    f.write(content)

print("Carefully removed all typedef_relations references from generator.py")