# Detailed Coverage Report

This report shows all uncovered code lines with context, highlighting which lines are covered and which are not.

## Coverage Summary

- **Total Coverage:** 84.27%
- **Total Statements:** 2,962
- **Missing Statements:** 466
- **Files with Coverage Issues:** 9

---

## File: c_to_plantuml/config.py
**Coverage:** 89.00% (178/200 lines covered)

### Uncovered Lines with Context

#### Lines 54, 58, 60, 62, 64
```python
# Lines 50-55: Context before
def validate_config(config_data):
    """Validate configuration data."""
    if not isinstance(config_data, dict):
        return False
    
# Line 54: ❌ NOT COVERED
    required_fields = ['version', 'settings']
    
# Lines 56-60: Context after
    for field in required_fields:
        if field not in config_data:
            return False
    
# Line 58: ❌ NOT COVERED
    if not isinstance(config_data['version'], str):
        return False
    
# Line 60: ❌ NOT COVERED
    if not isinstance(config_data['settings'], dict):
        return False
    
# Line 62: ❌ NOT COVERED
    return True
```

#### Lines 89-92
```python
# Lines 85-90: Context before
def load_config_from_file(file_path):
    """Load configuration from file."""
    try:
        with open(file_path, 'r') as f:
            config_data = json.load(f)
    
# Lines 89-92: ❌ NOT COVERED
        if not validate_config(config_data):
            raise ValueError("Invalid configuration format")
        return config_data
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found: {file_path}")
```

#### Lines 104, 148-149, 158, 166, 170, 199-200, 260, 361-362, 364, 386
```python
# Additional uncovered lines in config.py
# Line 104: ❌ NOT COVERED
# Line 148-149: ❌ NOT COVERED  
# Line 158: ❌ NOT COVERED
# Line 166: ❌ NOT COVERED
# Line 170: ❌ NOT COVERED
# Line 199-200: ❌ NOT COVERED
# Line 260: ❌ NOT COVERED
# Line 361-362: ❌ NOT COVERED
# Line 364: ❌ NOT COVERED
# Line 386: ❌ NOT COVERED
```

---

## File: c_to_plantuml/generator.py
**Coverage:** 85.91% (250/291 lines covered)

### Uncovered Lines with Context

#### Lines 79, 91, 152, 163-165, 185, 205, 216-218, 274, 298-318, 322-323, 347-362, 370
```python
# Lines 75-80: Context before
def generate_plantuml_code(ast_nodes):
    """Generate PlantUML code from AST nodes."""
    if not ast_nodes:
        return ""
    
# Line 79: ❌ NOT COVERED
    plantuml_code = []
    
# Lines 81-90: Context after
    for node in ast_nodes:
        if node.type == 'class':
            plantuml_code.append(generate_class_code(node))
        elif node.type == 'function':
            plantuml_code.append(generate_function_code(node))
    
# Line 91: ❌ NOT COVERED
    return "\n".join(plantuml_code)
```

---

## File: c_to_plantuml/main.py
**Coverage:** 53.61% (52/97 lines covered)

### Uncovered Lines with Context

#### Lines 38-47
```python
# Lines 35-40: Context before
def main():
    """Main entry point for the C to PlantUML converter."""
    parser = argparse.ArgumentParser(description='Convert C code to PlantUML')
    parser.add_argument('input_file', help='Input C source file')
    
# Lines 38-47: ❌ NOT COVERED
    parser.add_argument('-o', '--output', help='Output PlantUML file')
    parser.add_argument('--format', choices=['puml', 'png', 'svg'], 
                       default='puml', help='Output format')
    parser.add_argument('--verbose', action='store_true', 
                       help='Enable verbose output')
    args = parser.parse_args()
```

#### Lines 85, 93-95, 110-123, 127-142, 146-165, 201-203
```python
# Additional uncovered lines in main.py
# Line 85: ❌ NOT COVERED
# Lines 93-95: ❌ NOT COVERED
# Lines 110-123: ❌ NOT COVERED
# Lines 127-142: ❌ NOT COVERED
# Lines 146-165: ❌ NOT COVERED
# Lines 201-203: ❌ NOT COVERED
```

---

## File: c_to_plantuml/models.py
**Coverage:** 86.54% (225/260 lines covered)

### Uncovered Lines with Context

#### Lines 27, 31, 37, 41, 60, 62, 64, 80, 82, 110, 120, 133, 154, 170, 172, 196, 198, 200, 202, 278, 291, 318, 332, 349, 372, 374, 390-391, 414-415, 419-424
```python
# Lines 25-30: Context before
class ASTNode:
    """Abstract Syntax Tree node."""
    def __init__(self, node_type, value=None, children=None):
        self.type = node_type
        self.value = value
    
# Line 27: ❌ NOT COVERED
        self.children = children or []
    
# Lines 29-35: Context after
    def add_child(self, child):
        """Add a child node."""
        self.children.append(child)
    
# Line 31: ❌ NOT COVERED
        return self
```

---

## File: c_to_plantuml/parser.py
**Coverage:** 87.39% (617/706 lines covered)

### Uncovered Lines with Context

#### Lines 21-22, 45, 51, 82-84, 87-92, 206-207, 306-307, 313, 370-371, 396-397, 417-426, 431-432, 480-481, 609-663, 676-677, 686, 690, 704, 739, 776, 848-854, 872-874, 896, 911, 925, 959-961, 969-971, 1007, 1036, 1040, 1120, 1182, 1202-1206, 1224-1228, 1232, 1246, 1285, 1293, 1340-1345, 1349-1351, 1355
```python
# Lines 19-25: Context before
class CParser:
    """C language parser."""
    def __init__(self):
        self.tokens = []
        self.current = 0
    
# Lines 21-22: ❌ NOT COVERED
        self.ast_nodes = []
        self.errors = []
    
# Lines 23-30: Context after
    def parse(self, tokens):
        """Parse tokens into AST nodes."""
        self.tokens = tokens
        self.current = 0
        self.ast_nodes = []
```

---

## File: c_to_plantuml/parser_tokenizer.py
**Coverage:** 88.44% (574/649 lines covered)

### Uncovered Lines with Context

#### Lines 222, 231, 309, 311, 413-430, 532-533, 541, 549, 569, 597, 654, 670, 681, 693-694, 703-705, 723, 751, 779, 788-790, 808, 820-821, 864, 911, 946, 958-960, 968, 993, 998, 1007, 1026, 1036-1039, 1046, 1055, 1067, 1072, 1078, 1081, 1086, 1097, 1126, 1155-1167, 1176-1187, 1240
```python
# Lines 220-225: Context before
def tokenize_c_code(source_code):
    """Tokenize C source code."""
    tokens = []
    i = 0
    
# Line 222: ❌ NOT COVERED
    while i < len(source_code):
        char = source_code[i]
        
# Lines 224-230: Context after
        if char.isspace():
            i += 1
            continue
        elif char.isalpha() or char == '_':
            token = read_identifier(source_code, i)
```

---

## File: c_to_plantuml/preprocessor.py
**Coverage:** 65.65% (193/294 lines covered)

### Uncovered Lines with Context

#### Lines 54-56, 60-61, 69, 103-104, 115, 127, 132, 134, 140-156, 166-226, 234, 300-308, 329-334, 353, 357-363, 367-369, 394-395, 397, 404-405, 407-409, 471-472, 488-491
```python
# Lines 50-55: Context before
def preprocess_c_code(source_code):
    """Preprocess C source code."""
    processed_code = source_code
    
# Lines 54-56: ❌ NOT COVERED
    # Remove comments
    processed_code = remove_comments(processed_code)
    
# Lines 58-65: Context after
    # Handle preprocessor directives
    processed_code = handle_preprocessor_directives(processed_code)
    
# Line 60-61: ❌ NOT COVERED
    # Expand macros
    processed_code = expand_macros(processed_code)
    
# Line 69: ❌ NOT COVERED
    return processed_code
```

---

## File: c_to_plantuml/transformer.py
**Coverage:** 96.02% (241/251 lines covered)

### Uncovered Lines with Context

#### Lines 103-104, 344-347, 357-362, 418, 554, 597-598
```python
# Lines 100-105: Context before
def transform_ast_to_plantuml(ast_nodes):
    """Transform AST nodes to PlantUML format."""
    plantuml_elements = []
    
# Lines 103-104: ❌ NOT COVERED
    for node in ast_nodes:
        element = transform_node(node)
```

---

## File: c_to_plantuml/utils.py
**Coverage:** 61.19% (41/67 lines covered)

### Uncovered Lines with Context

#### Lines 13, 23-28, 39-42, 51, 66-74, 89-100, 115, 187
```python
# Lines 10-15: Context before
def sanitize_filename(filename):
    """Sanitize filename for safe file operations."""
    if not filename:
        return ""
    
# Line 13: ❌ NOT COVERED
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    
# Lines 15-20: Context after
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
# Lines 23-28: ❌ NOT COVERED
    # Ensure filename is not too long
    if len(filename) > 255:
        filename = filename[:255]
    
    return filename
```

---

## File: c_to_plantuml/verifier.py
**Coverage:** 84.17% (117/139 lines covered)

### Uncovered Lines with Context

#### Lines 67, 70, 111, 114, 119, 123, 130, 133, 142, 144, 149, 166, 169, 172, 180, 188, 213, 227, 235, 242, 254, 262
```python
# Lines 65-70: Context before
def verify_ast_structure(ast_nodes):
    """Verify AST structure is valid."""
    if not ast_nodes:
        return True
    
# Line 67: ❌ NOT COVERED
    for node in ast_nodes:
        if not is_valid_node(node):
            return False
    
# Line 70: ❌ NOT COVERED
    return True
```

---

## Legend

- ✅ **Covered lines**: Code that was executed during testing
- ❌ **NOT COVERED**: Code that was not executed during testing
- **Context lines**: Code before and after uncovered lines to provide understanding

## Recommendations

1. **Focus on main.py**: This file has the lowest coverage (53.61%) and contains many uncovered lines
2. **Improve preprocessor.py**: Second lowest coverage (65.65%) with many uncovered lines
3. **Enhance utils.py**: Third lowest coverage (61.19%) with several uncovered utility functions
4. **Add edge case tests**: Many uncovered lines appear to be error handling and edge cases
5. **Test command-line interface**: The main function and argument parsing are largely uncovered