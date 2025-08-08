"""
Feature tests for transformer functionality

Tests advanced transformer features and integration scenarios.
"""

import json
import os
import tempfile
from pathlib import Path

from tests.feature.base import BaseFeatureTest

# Add src directory to path for new package structure
import sys
import os
from pathlib import Path

# Get the absolute path to the src directory 
current_file = Path(__file__).resolve()
test_dir = current_file.parent
project_root = test_dir.parent.parent
src_path = project_root / "src"

if src_path.exists():
    sys.path.insert(0, str(src_path))
# Also add tests directory for test utilities
tests_path = project_root / "tests"
if tests_path.exists():
    sys.path.insert(0, str(tests_path))

from c2puml.parser import Parser
from c2puml.transformer import Transformer


class TestTransformerFeatures(BaseFeatureTest):
    """Test advanced transformer features"""

    def test_transform_complex_project_with_filters(self):
        """Test transforming a complex project with various filters"""

        # Create a complex test project
        main_c = """
#include <stdio.h>
#include <stdlib.h>
#include "utils.h"
#include "config.h"

#define MAX_SIZE 100
#define DEBUG_MODE 1
#define LEGACY_FLAG 0

typedef struct {
    int id;
    char name[64];
    float value;
} DataStruct;

typedef struct {
    int legacy_id;
    char legacy_data[32];
} LegacyStruct;

int global_counter = 0;
int legacy_var = 999;

void process_data(DataStruct* data) {
    data->value *= 2.0;
}

void legacy_function() {
    printf("Legacy function\\n");
}

int main() {
    DataStruct data = {1, "test", 3.14};
    process_data(&data);
    return 0;
}
"""

        utils_h = """
#ifndef UTILS_H
#define UTILS_H

void utility_function();
void legacy_util();

#endif
"""

        config_h = """
#ifndef CONFIG_H
#define CONFIG_H

#define CONFIG_VERSION "1.0"

typedef struct {
    char name[50];
    int timeout;
} Config;

void load_config();

#endif
"""

        # Create temporary project
        temp_project = self.create_temp_project({
            "main.c": main_c,
            "utils.h": utils_h,
            "config.h": config_h
        })

        # Configuration with complex transformations
        config = {
            "file_filters": {
                "include": ["*.c", "*.h"],
                "exclude": ["*test*"]
            },
            "transformations": {
                "remove": {
                    "functions": ["legacy_.*"],
                    "structs": ["Legacy.*"],
                    "globals": ["legacy_.*"]
                },
                "rename": {
                    "functions": {
                        "process_(.*)": "handle_$1"
                    },
                    "structs": {
                        "DataStruct": "ProcessedData"
                    }
                }
            }
        }

        # Parse and transform
        parser = Parser()
        transformer = Transformer()
        
        project_model = parser.parse_project(temp_project, config)
        transformed_model = transformer.transform(project_model, config)

        # Validate transformations
        self.assertIsNotNone(transformed_model)
        
        # Check that legacy items were removed
        main_file = transformed_model.files.get("main.c")
        self.assertIsNotNone(main_file)
        
        function_names = [f.name for f in main_file.functions]
        self.assertNotIn("legacy_function", function_names)
        
        # Check that items were renamed
        self.assertIn("handle_data", function_names)
        
        struct_names = [s.name for s in main_file.structs]
        self.assertNotIn("LegacyStruct", struct_names)
        self.assertIn("ProcessedData", struct_names)

    def test_transform_with_include_relations(self):
        """Test transformer with include relationship processing"""
        
        main_c = """
#include "types.h"
#include "functions.h"

int main() {
    MyStruct data;
    process_struct(&data);
    return 0;
}
"""

        types_h = """
#ifndef TYPES_H
#define TYPES_H

typedef struct {
    int id;
    char name[32];
} MyStruct;

#endif
"""

        functions_h = """
#ifndef FUNCTIONS_H
#define FUNCTIONS_H

#include "types.h"

void process_struct(MyStruct* s);

#endif
"""

        temp_project = self.create_temp_project({
            "main.c": main_c,
            "types.h": types_h,
            "functions.h": functions_h
        })

        config = {
            "include_depth": 2,
            "transformations": {
                "rename": {
                    "structs": {
                        "MyStruct": "RenamedStruct"
                    }
                }
            }
        }

        parser = Parser()
        transformer = Transformer()
        
        project_model = parser.parse_project(temp_project, config)
        transformed_model = transformer.transform(project_model, config)

        # Validate include relationships are preserved
        self.assertIsNotNone(transformed_model)
        self.assertTrue(len(transformed_model.files) >= 2)  # At least main.c and headers

    def test_transform_with_renaming(self):
        """Test comprehensive renaming transformations"""
        
        source_code = """
#include <stdio.h>

#define OLD_MACRO 100
#define ANOTHER_MACRO 200

typedef struct {
    int old_field;
    char data[50];
} OldStruct;

int old_global = 42;

void old_function() {
    printf("Old function\\n");
}

void another_function() {
    printf("Another function\\n");
}

int main() {
    OldStruct s;
    old_function();
    return 0;
}
"""

        temp_project = self.create_temp_project({"main.c": source_code})

        config = {
            "transformations": {
                "rename": {
                    "functions": {
                        "^old_(.*)$": "new_$1"
                    },
                    "structs": {
                        "^Old(.*)$": "Modern$1"
                    },
                    "macros": {
                        "OLD_MACRO": "NEW_MACRO"
                    },
                    "globals": {
                        "old_global": "new_global"
                    }
                }
            }
        }

        parser = Parser()
        transformer = Transformer()
        
        project_model = parser.parse_project(temp_project, config)
        transformed_model = transformer.transform(project_model, config)

        main_file = transformed_model.files.get("main.c")
        self.assertIsNotNone(main_file)

        # Check function renaming
        function_names = [f.name for f in main_file.functions]
        self.assertIn("new_function", function_names)
        self.assertNotIn("old_function", function_names)
        self.assertIn("another_function", function_names)  # Should remain unchanged

        # Check struct renaming
        struct_names = [s.name for s in main_file.structs]
        self.assertIn("ModernStruct", struct_names)
        self.assertNotIn("OldStruct", struct_names)

    def test_transform_with_additions(self):
        """Test adding new elements via transformations"""
        
        source_code = """
#include <stdio.h>

typedef struct {
    int id;
} SimpleStruct;

void existing_function() {
    printf("Existing\\n");
}

int main() {
    return 0;
}
"""

        temp_project = self.create_temp_project({"main.c": source_code})

        config = {
            "transformations": {
                "add": {
                    "functions": ["new_added_function"],
                    "macros": ["ADDED_MACRO"],
                    "globals": ["added_global"]
                }
            }
        }

        parser = Parser()
        transformer = Transformer()
        
        project_model = parser.parse_project(temp_project, config)
        transformed_model = transformer.transform(project_model, config)

        main_file = transformed_model.files.get("main.c")
        self.assertIsNotNone(main_file)

        # Check that original elements are preserved
        function_names = [f.name for f in main_file.functions]
        self.assertIn("existing_function", function_names)
        self.assertIn("main", function_names)

    def test_transform_with_removals(self):
        """Test removing elements via transformations"""
        
        source_code = """
#include <stdio.h>

#define REMOVE_ME 1
#define KEEP_ME 2

typedef struct {
    int id;
} RemoveStruct;

typedef struct {
    int value;
} KeepStruct;

void remove_function() {
    printf("Remove me\\n");
}

void keep_function() {
    printf("Keep me\\n");
}

int remove_global = 100;
int keep_global = 200;

int main() {
    return 0;
}
"""

        temp_project = self.create_temp_project({"main.c": source_code})

        config = {
            "transformations": {
                "remove": {
                    "functions": ["remove_.*"],
                    "structs": ["Remove.*"],
                    "macros": ["REMOVE_.*"],
                    "globals": ["remove_.*"]
                }
            }
        }

        parser = Parser()
        transformer = Transformer()
        
        project_model = parser.parse_project(temp_project, config)
        transformed_model = transformer.transform(project_model, config)

        main_file = transformed_model.files.get("main.c")
        self.assertIsNotNone(main_file)

        # Check removals
        function_names = [f.name for f in main_file.functions]
        self.assertNotIn("remove_function", function_names)
        self.assertIn("keep_function", function_names)
        self.assertIn("main", function_names)

        struct_names = [s.name for s in main_file.structs]
        self.assertNotIn("RemoveStruct", struct_names)
        self.assertIn("KeepStruct", struct_names)

    def test_transform_complex_regex_patterns(self):
        """Test complex regex pattern matching in transformations"""
        
        source_code = """
#include <stdio.h>

// Functions with different patterns
void func_v1_process() { }
void func_v2_process() { }
void func_v1_cleanup() { }
void other_function() { }

// Structs with patterns
typedef struct {
    int data;
} DataV1Struct;

typedef struct {
    int info;
} DataV2Struct;

typedef struct {
    int other;
} OtherStruct;

int main() {
    return 0;
}
"""

        temp_project = self.create_temp_project({"main.c": source_code})

        config = {
            "transformations": {
                "remove": {
                    "functions": [".*_v1_.*"]
                },
                "rename": {
                    "functions": {
                        "^func_v2_(.*)$": "new_$1"
                    },
                    "structs": {
                        "^Data(.*)Struct$": "Processed$1"
                    }
                }
            }
        }

        parser = Parser()
        transformer = Transformer()
        
        project_model = parser.parse_project(temp_project, config)
        transformed_model = transformer.transform(project_model, config)

        main_file = transformed_model.files.get("main.c")
        self.assertIsNotNone(main_file)

        function_names = [f.name for f in main_file.functions]
        
        # Check v1 functions removed
        self.assertNotIn("func_v1_process", function_names)
        self.assertNotIn("func_v1_cleanup", function_names)
        
        # Check v2 function renamed
        self.assertIn("new_process", function_names)
        self.assertNotIn("func_v2_process", function_names)
        
        # Check other function preserved
        self.assertIn("other_function", function_names)

    def test_transform_error_handling(self):
        """Test transformer error handling scenarios"""
        
        source_code = """
#include <stdio.h>

void valid_function() {
    printf("Valid\\n");
}

int main() {
    return 0;
}
"""

        temp_project = self.create_temp_project({"main.c": source_code})

        # Test with invalid regex patterns
        config = {
            "transformations": {
                "rename": {
                    "functions": {
                        "[invalid_regex": "replacement"  # Invalid regex
                    }
                }
            }
        }

        parser = Parser()
        transformer = Transformer()
        
        project_model = parser.parse_project(temp_project, config)
        
        # Should handle invalid regex gracefully
        try:
            transformed_model = transformer.transform(project_model, config)
            # Should either succeed with no changes or handle error gracefully
            self.assertIsNotNone(transformed_model)
        except Exception as e:
            # If it raises an exception, it should be a meaningful one
            self.assertIn("regex", str(e).lower())

    def test_transform_integration_with_parser_and_generator(self):
        """Test transformer integration with full pipeline"""
        
        main_c = """
#include <stdio.h>
#include "data.h"

void process_main_data(MainData* data) {
    data->processed = 1;
}

int main() {
    MainData data = {0, "test", 0};
    process_main_data(&data);
    return 0;
}
"""

        data_h = """
#ifndef DATA_H
#define DATA_H

typedef struct {
    int id;
    char name[50];
    int processed;
} MainData;

void init_data(MainData* data);

#endif
"""

        temp_project = self.create_temp_project({
            "main.c": main_c,
            "data.h": data_h
        })

        config = {
            "include_depth": 2,
            "transformations": {
                "rename": {
                    "functions": {
                        "process_(.*)": "handle_$1"
                    },
                    "structs": {
                        "MainData": "ProcessedData"
                    }
                }
            }
        }

        # Full pipeline test
        parser = Parser()
        transformer = Transformer()
        
        # Parse
        project_model = parser.parse_project(temp_project, config)
        self.assertIsNotNone(project_model)
        
        # Transform
        transformed_model = transformer.transform(project_model, config)
        self.assertIsNotNone(transformed_model)
        
        # Validate transformation results
        main_file = transformed_model.files.get("main.c")
        self.assertIsNotNone(main_file)
        
        function_names = [f.name for f in main_file.functions]
        self.assertIn("handle_main_data", function_names)
        self.assertNotIn("process_main_data", function_names)

    def test_include_filters_with_filtered_header(self):
        """Test include filters with filtered header files"""
        
        main_c = """
#include <stdio.h>
#include "keep.h"
#include "filter.h"

int main() {
    KeepStruct k;
    FilterStruct f;
    return 0;
}
"""

        keep_h = """
#ifndef KEEP_H
#define KEEP_H

typedef struct {
    int keep_data;
} KeepStruct;

#endif
"""

        filter_h = """
#ifndef FILTER_H
#define FILTER_H

typedef struct {
    int filter_data;
} FilterStruct;

#endif
"""

        temp_project = self.create_temp_project({
            "main.c": main_c,
            "keep.h": keep_h,
            "filter.h": filter_h
        })

        config = {
            "file_filters": {
                "include": ["main.c", "keep.h"]
            },
            "include_depth": 2,
            "transformations": {
                "rename": {
                    "structs": {
                        "KeepStruct": "RenamedKeepStruct"
                    }
                }
            }
        }

        parser = Parser()
        transformer = Transformer()
        
        project_model = parser.parse_project(temp_project, config)
        transformed_model = transformer.transform(project_model, config)

        # Should only process files that match the filter
        self.assertIsNotNone(transformed_model)
        self.assertIn("main.c", transformed_model.files)
        
        # filter.h should be excluded by file filter
        # Note: This test validates that transformations work with file filtering