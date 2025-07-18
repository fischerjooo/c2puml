# Model Filtering and Manipulation Guide

This guide explains the enhanced JSON configuration input system that allows you to filter, transform, and manipulate parsed C model files using regex patterns. This extends the capabilities beyond just C file input filtering, enabling sophisticated pump model manipulation.

## Overview

The enhanced configuration system supports:
- **File Filtering**: Filter out or include specific files using regex patterns
- **Element Filtering**: Filter structs, enums, functions, and global variables
- **Transformations**: Rename elements using regex pattern matching and replacement
- **Additions**: Add new elements to specific files or all files
- **Regex Support**: All filtering operations support regular expressions for flexible matching

## Configuration Structure

```json
{
  // Standard configuration options
  "project_name": "Your_Project_Name",
  "project_roots": ["./path/to/source"],
  "c_file_prefixes": [],
  "recursive": true,
  "model_output_path": "./output_model.json",
  "output_dir": "./plantuml_output",

  // New filtering and manipulation options
  "file_filters": { /* File-level filtering */ },
  "element_filters": { /* Element-level filtering */ },
  "transformations": { /* Renaming and transformations */ },
  "additions": { /* Add new elements */ }
}
```

## File Filtering

Filter entire files based on their paths using regex patterns:

```json
"file_filters": {
  "files": {
    "include": [
      ".*\\.c$",        // Only .c files
      ".*\\.h$",        // Only .h files
      ".*pump.*"        // Files containing "pump"
    ],
    "exclude": [
      ".*test.*",       // Exclude test files
      ".*temp.*",       // Exclude temporary files
      ".*\\.tmp$",      // Exclude .tmp files
      ".*_deprecated.*" // Exclude deprecated files
    ]
  }
}
```

## Element Filtering

Filter individual elements within files using regex patterns:

### Struct Filtering
```json
"element_filters": {
  "structs": {
    "include": [
      "^[A-Z].*",       // Structs starting with uppercase
      ".*_t$",          // Structs ending with _t
      "pump_.*"         // Pump-related structs
    ],
    "exclude": [
      ".*_internal.*",  // Exclude internal structs
      ".*_deprecated.*" // Exclude deprecated structs
    ]
  }
}
```

### Enum Filtering
```json
"element_filters": {
  "enums": {
    "include": [
      ".*_enum$",       // Enums ending with _enum
      "^E_.*",          // Enums starting with E_
      "pump_.*_state"   // Pump state enums
    ],
    "exclude": [
      ".*_old.*"        // Exclude old enums
    ]
  }
}
```

### Function Filtering
```json
"element_filters": {
  "functions": {
    "include": [
      "^public_.*",     // Public functions
      "^api_.*",        // API functions
      "pump_.*"         // Pump functions
    ],
    "exclude": [
      "^_.*",           // Private functions (starting with _)
      ".*_private.*",   // Functions with _private in name
      ".*_test.*"       // Test functions
    ]
  }
}
```

### Global Variable Filtering
```json
"element_filters": {
  "globals": {
    "include": [
      "^g_.*",          // Global variables with g_ prefix
      ".*_config$",     // Configuration variables
      "pump_.*"         // Pump-related globals
    ],
    "exclude": [
      ".*_debug.*"      // Debug variables
    ]
  }
}
```

## Transformations (Renaming)

Rename elements using regex patterns and replacement strings:

### Struct Transformations
```json
"transformations": {
  "structs": {
    "^old_(.*)": "new_\\1",           // old_name -> new_name
    "(.*)_struct$": "\\1_t",          // name_struct -> name_t
    "^legacy_": "",                   // Remove "legacy_" prefix
    "pump_(.*)_config": "\\1_cfg"     // pump_xxx_config -> xxx_cfg
  }
}
```

### Enum Transformations
```json
"transformations": {
  "enums": {
    "^old_(.*)_enum": "\\1_e",        // old_name_enum -> name_e
    "(.*)_status": "\\1_state",       // name_status -> name_state
    "pump_(.*)_mode": "pump_\\1_state" // pump_xxx_mode -> pump_xxx_state
  }
}
```

### Function Transformations
```json
"transformations": {
  "functions": {
    "^legacy_(.*)": "modern_\\1",     // legacy_func -> modern_func
    "(.*)_impl$": "\\1",              // func_impl -> func
    "^internal_(.*)": "_\\1",         // internal_func -> _func
    "pump_(.*)_set": "pump_set_\\1"   // pump_xxx_set -> pump_set_xxx
  }
}
```

## Additions

Add new elements to specific files or all files:

### Adding Structs
```json
"additions": {
  "structs": [
    {
      "name": "pump_config_t",
      "typedef_name": "pump_config_t",
      "fields": [
        {
          "name": "enabled",
          "type": "bool"
        },
        {
          "name": "max_pressure",
          "type": "float"
        },
        {
          "name": "name",
          "type": "char",
          "array_size": "64"
        }
      ],
      "target_files": [
        ".*pump.*\\.h$",       // Add to pump header files
        ".*config.*\\.h$"      // Add to config header files
      ]
    }
  ]
}
```

### Adding Enums
```json
"additions": {
  "enums": [
    {
      "name": "pump_state_e",
      "typedef_name": "pump_state_t",
      "values": [
        "PUMP_IDLE",
        "PUMP_RUNNING",
        "PUMP_ERROR",
        "PUMP_MAINTENANCE"
      ],
      "target_files": [
        ".*pump.*"             // Add to all pump-related files
      ]
    }
  ]
}
```

### Adding Functions
```json
"additions": {
  "functions": [
    {
      "name": "pump_initialize",
      "return_type": "int",
      "parameters": [
        {
          "name": "config",
          "type": "pump_config_t*"
        }
      ],
      "is_static": false,
      "target_files": [
        ".*pump.*\\.c$"        // Add to pump source files
      ]
    }
  ]
}
```

## Usage Examples

### 1. Using Enhanced Configuration
```bash
# Analyze with filtering and transformation
python -m c_to_plantuml.main config enhanced_config.json
```

### 2. Filtering Existing Models
```bash
# Apply filters to existing JSON model
python -m c_to_plantuml.main filter existing_model.json filter_config.json -o filtered_model.json
```

### 3. Pump-Specific Configuration Example
```json
{
  "project_name": "Pump_Control_System",
  "project_roots": ["./src"],
  "model_output_path": "./pump_model.json",
  "output_dir": "./pump_plantuml",
  
  "file_filters": {
    "files": {
      "include": [".*pump.*", ".*control.*", ".*sensor.*"],
      "exclude": [".*test.*", ".*mock.*"]
    }
  },
  
  "element_filters": {
    "functions": {
      "include": ["pump_.*", "control_.*", "sensor_.*"],
      "exclude": [".*_test.*", ".*_debug.*"]
    }
  },
  
  "transformations": {
    "structs": {
      "pump_(.*)_data": "\\1_info",
      "legacy_pump_(.*)": "pump_\\1"
    }
  },
  
  "additions": {
    "structs": [
      {
        "name": "pump_runtime_t",
        "fields": [
          {"name": "current_state", "type": "pump_state_t"},
          {"name": "last_maintenance", "type": "time_t"},
          {"name": "operating_hours", "type": "uint32_t"}
        ],
        "target_files": [".*pump.*\\.h$"]
      }
    ]
  }
}
```

## Regex Pattern Examples

### Common Patterns
- `^prefix_.*` - Starts with "prefix_"
- `.*_suffix$` - Ends with "_suffix"
- `.*keyword.*` - Contains "keyword"
- `^[A-Z].*` - Starts with uppercase letter
- `.*[0-9]+.*` - Contains numbers
- `(group1)_(group2)` - Capture groups for replacement

### Replacement Patterns
- `\\1` - First capture group
- `\\2` - Second capture group
- `prefix_\\1_suffix` - Add prefix and suffix to capture group

## Performance Considerations

- All regex patterns are pre-compiled for optimal performance
- Filtering happens after parsing, so complex filters don't affect parse time
- Consider using specific patterns rather than broad matches for better performance

## Error Handling

- Invalid regex patterns will cause compilation errors at startup
- Missing fields in additions will be handled gracefully
- File path matching failures will be logged but won't stop processing

## Best Practices

1. **Start Simple**: Begin with basic include/exclude patterns
2. **Test Patterns**: Use regex tools to test your patterns before applying
3. **Use Specific Targets**: Use `target_files` in additions to avoid unnecessary additions
4. **Document Patterns**: Use comments in JSON to explain complex regex patterns
5. **Backup Models**: Always keep backups of original models before filtering

This enhanced system allows for sophisticated manipulation of the parsed C model, enabling you to create customized views and transformations that go far beyond simple C file filtering.