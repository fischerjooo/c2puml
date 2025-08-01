# PlantUML Parser Fix Workflow

## Issues Identified

### 1. Array Bracket Spacing Issues
- [x] Function parameters: `int data [ ]` → `int data[]` ✅ FIXED
- [x] Global variables: `math_operation_t global_math_ops [ 10 ]` → `math_operation_t global_math_ops[10]` ✅ FIXED

### 2. Function Pointer Type Parsing Issues
- [ ] Duplicate identifiers: `int ( * init_func ) ( void * ) init_func`
- [ ] Type name inclusion: `int(* math_op_t)(int , int)`

### 3. Struct Field Parsing Issues
- [ ] Array field formatting: `char[64] name` → `char name[64]`
- [ ] Array field formatting: `math_operation_t[5] operations` → `math_operation_t operations[5]`

### 4. Enum Parsing Issues
- [ ] Concatenated values: `NET_STATUS_DISCONNECTED , NET_STATUS_CONNECTING , ...`
- [ ] Should be separate lines for each enum value

### 5. Typedef Parsing Issues
- [ ] Array typedefs: `MyComplexPtr MyComplexArray[10]` → `MyComplexPtr[10]`
- [ ] Complex typedefs not parsed correctly

### 6. Anonymous Struct/Union Issues
- [ ] Poor naming: `__anonymous_struct__`

## Testing Strategy
1. Run `./scripts/run_example.sh` after each fix
2. Check validation results
3. Examine specific .puml files for improvements
4. Compare with source C files

## Fix Order
1. Array bracket spacing (function parameters & global variables)
2. Function pointer parsing
3. Struct field parsing
4. Enum parsing
5. Typedef parsing
6. Anonymous struct/union naming