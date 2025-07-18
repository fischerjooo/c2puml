# Multi-Configuration System Guide

## Overview

The model transformation system has been enhanced to support multiple configuration files based on logical groupings. This allows for better organization, reusability, and modular configuration management.

## 🔄 Renamed Components

### ModelTransformer (formerly ModelFilter)
- **File**: `c_to_plantuml/manipulators/model_transformer.py`
- **Class**: `ModelTransformer` (was `ModelFilter`)
- **Capabilities**: 
  - ✅ File filtering
  - ✅ Element filtering  
  - ✅ Transformations (renaming)
  - ✅ Additions (injection)
  - ✅ Multi-config support

The name better reflects the comprehensive transformation capabilities beyond just filtering.

## 📁 Configuration File Organization

### Logical Groupings

Split your configuration into focused, reusable files:

#### 1. **Project Configuration** (`project_config.json`)
Basic project settings and analysis parameters:
```json
{
  "project_name": "My_Project",
  "project_roots": ["./src"],
  "c_file_prefixes": [],
  "recursive": true,
  "model_output_path": "./project_model.json",
  "output_dir": "./plantuml_output"
}
```

#### 2. **File Filters** (`file_filters.json`)
File-level inclusion/exclusion patterns:
```json
{
  "file_filters": {
    "files": {
      "include": [".*\\.c$", ".*\\.h$"],
      "exclude": [".*test.*", ".*temp.*"]
    }
  }
}
```

#### 3. **Element Filters** (`element_filters.json`)
Element-level filtering for structs, enums, functions:
```json
{
  "element_filters": {
    "structs": {
      "include": ["^[A-Z].*", ".*_t$"],
      "exclude": [".*_internal.*"]
    },
    "functions": {
      "include": ["^public_.*", "^api_.*"],
      "exclude": ["^_.*", ".*_private.*"]
    }
  }
}
```

#### 4. **Transformations** (`transformations.json`)
Regex-based renaming and modifications:
```json
{
  "transformations": {
    "structs": {
      "^old_(.*)": "new_\\1",
      "(.*)_struct$": "\\1_t"
    },
    "functions": {
      "^legacy_(.*)": "modern_\\1"
    }
  }
}
```

#### 5. **Domain-Specific Additions** (`pump_additions.json`)
Add domain-specific elements:
```json
{
  "additions": {
    "structs": [
      {
        "name": "pump_config_t",
        "fields": [...],
        "target_files": [".*pump.*\\.h$"]
      }
    ],
    "enums": [
      {
        "name": "pump_state_e",
        "values": ["PUMP_IDLE", "PUMP_RUNNING"],
        "target_files": [".*pump.*"]
      }
    ]
  }
}
```

#### 6. **General Additions** (`general_additions.json`)
Common utility structures:
```json
{
  "additions": {
    "structs": [
      {
        "name": "error_info_t",
        "fields": [...],
        "target_files": [".*\\.h$"]
      }
    ]
  }
}
```

## 🚀 Usage Methods

### Method 1: Standalone Multi-Config Filtering

Apply multiple transformation configs to an existing model:

```bash
# Transform with multiple config files
python -m c_to_plantuml.main filter model.json \
  config/file_filters.json \
  config/element_filters.json \
  config/transformations.json \
  config/pump_additions.json \
  -o transformed_model.json
```

### Method 2: Referenced Configurations

Reference multiple transformation configs from a main config:

**main_config.json:**
```json
{
  "project_name": "Pump_System",
  "project_roots": ["./src"],
  "model_output_path": "./pump_model.json",
  "output_dir": "./plantuml_output",
  
  "transformation_configs": [
    "config/file_filters.json",
    "config/element_filters.json", 
    "config/transformations.json",
    "config/pump_additions.json",
    "config/general_additions.json"
  ]
}
```

```bash
# Use main config with referenced transformation configs
python -m c_to_plantuml.main config main_config.json
```

### Method 3: Inline + External Configs

Combine inline transformations with external configs:

```json
{
  "project_name": "Mixed_Config",
  "project_roots": ["./src"],
  
  // Inline transformations
  "element_filters": {
    "functions": {
      "exclude": [".*_test.*"]
    }
  },
  
  // External transformation configs
  "transformation_configs": [
    "config/pump_additions.json"
  ]
}
```

## 🔧 Configuration Merging

### Merging Rules

1. **Dictionaries**: Deep merged (nested structures combined)
2. **Lists**: Concatenated (all items included)
3. **Conflicts**: Later configs override earlier ones

### Example Merging

**Config 1:**
```json
{
  "element_filters": {
    "structs": {
      "include": [".*_t$"]
    }
  }
}
```

**Config 2:**
```json
{
  "element_filters": {
    "structs": {
      "exclude": [".*_internal.*"]
    },
    "functions": {
      "include": ["^api_.*"]
    }
  }
}
```

**Merged Result:**
```json
{
  "element_filters": {
    "structs": {
      "include": [".*_t$"],
      "exclude": [".*_internal.*"]
    },
    "functions": {
      "include": ["^api_.*"]
    }
  }
}
```

## 📋 Best Practices

### 1. **Logical Separation**
- Keep different concerns in separate files
- Use descriptive filenames
- Group related transformations together

### 2. **Reusability**
- Create reusable filter sets for common scenarios
- Share configs across projects
- Version control your configurations

### 3. **Order Matters**
- List transformation configs in logical order
- Apply filters before transformations
- Apply additions last

### 4. **File Organization**
```
project/
├── config/
│   ├── project_config.json
│   ├── file_filters.json
│   ├── element_filters.json
│   ├── transformations.json
│   ├── pump_additions.json
│   ├── general_additions.json
│   └── complete_config.json
├── src/
└── output/
```

### 5. **Testing Configurations**
```bash
# Test individual configs
python -m c_to_plantuml.main filter model.json config/file_filters.json -o test1.json

# Test combined configs
python -m c_to_plantuml.main filter model.json \
  config/file_filters.json config/element_filters.json -o test2.json

# Test complete workflow
python -m c_to_plantuml.main config config/complete_config.json
```

## 🎯 Example Workflows

### Pump System Development

1. **Base Analysis**:
   ```bash
   python -m c_to_plantuml.main analyze ./pump_src -o base_model.json
   ```

2. **Apply Pump Transformations**:
   ```bash
   python -m c_to_plantuml.main filter base_model.json \
     config/pump_filters.json \
     config/pump_transformations.json \
     config/pump_additions.json \
     -o pump_model.json
   ```

3. **Generate Documentation**:
   ```bash
   python -m c_to_plantuml.main generate pump_model.json -o pump_docs/
   ```

### Legacy Code Modernization

1. **Filter Legacy Elements**:
   ```json
   // legacy_filters.json
   {
     "element_filters": {
       "functions": {
         "include": ["^legacy_.*"]
       }
     }
   }
   ```

2. **Apply Modernization**:
   ```json
   // modernization.json
   {
     "transformations": {
       "functions": {
         "^legacy_(.*)": "modern_\\1"
       }
     }
   }
   ```

3. **Execute Transformation**:
   ```bash
   python -m c_to_plantuml.main filter legacy_model.json \
     config/legacy_filters.json \
     config/modernization.json \
     -o modernized_model.json
   ```

## 🚫 Common Pitfalls

1. **Over-Filtering**: Too restrictive filters can remove all content
2. **Path Issues**: Use relative paths from config directory
3. **Merge Conflicts**: Later configs override earlier ones
4. **Target Mismatches**: Ensure target_files patterns match actual files

## 🔍 Debugging

### Verbose Output
The system provides detailed logging:
```
Loading configuration: config/file_filters.json
Loading configuration: config/element_filters.json
Successfully merged 2 configuration files
Applied model transformations from 2 config(s)
```

### Validation
- Check file existence before referencing
- Validate regex patterns
- Test with small datasets first

This multi-configuration system enables powerful, modular transformation workflows while maintaining clean separation of concerns and maximum reusability.