#ifndef COMPLEX_H
#define COMPLEX_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

// Standard integer type definitions for the nasty macros
typedef uint8_t uint8;
typedef uint16_t uint16;
typedef uint32_t uint32;

// Nasty multiline macro with function-like behavior
#define COMPLEX_MACRO_FUNC(x, y, z) do { \
    int temp_var = (x) + (y) * (z); \
    if (temp_var > 100) { \
        temp_var = temp_var / 2; \
    } else { \
        temp_var = temp_var * 3; \
    } \
    (x) = temp_var; \
} while(0)

// Another nasty multiline macro with nested conditions
#define PROCESS_ARRAY(arr, size, callback) do { \
    for (int i = 0; i < (size); i++) { \
        int result = (callback)(&(arr)[i]); \
        if (result < 0) { \
            break; \
        } \
    } \
} while(0)

// Complex macro with stringification and concatenation
#define CREATE_FUNC_NAME(prefix, suffix) prefix##_##suffix
#define STRINGIFY(x) #x
#define TOSTRING(x) STRINGIFY(x)

// Nasty edge case: Complex multiline macro with type casting and bit shifting
/** *******************************************************************************************************************
 * \brief   Write uint 16 value in big endian format to uint8 array.
 *
 * \param[in]    value_u16   uint16 value
 * \param[out]   ptr_pau8    Pointer to uint8 array with at least 2 elements.
 *********************************************************************************************************************/
#define UTILS_U16_TO_U8ARR_BIG_ENDIAN(value_u16, ptr_pau8) \
{                                                                     \
    (ptr_pau8)[1U] = (uint8)((value_u16));                            \
    (ptr_pau8)[0U] = (uint8)((value_u16) >> 8U);                      \
}

// Additional nasty macro patterns for testing
#define UTILS_U32_TO_U8ARR_BIG_ENDIAN(value_u32, ptr_pau8) \
{                                                                     \
    (ptr_pau8)[3U] = (uint8)((value_u32));                            \
    (ptr_pau8)[2U] = (uint8)((value_u32) >> 8U);                      \
    (ptr_pau8)[1U] = (uint8)((value_u32) >> 16U);                     \
    (ptr_pau8)[0U] = (uint8)((value_u32) >> 24U);                     \
}

#define UTILS_U8ARR_TO_U16_BIG_ENDIAN(ptr_pau8) \
    (((uint16)((ptr_pau8)[0U]) << 8U) | ((uint16)((ptr_pau8)[1U])))

#define UTILS_U8ARR_TO_U32_BIG_ENDIAN(ptr_pau8) \
    (((uint32)((ptr_pau8)[0U]) << 24U) | \
     ((uint32)((ptr_pau8)[1U]) << 16U) | \
     ((uint32)((ptr_pau8)[2U]) << 8U) | \
     ((uint32)((ptr_pau8)[3U])))

// Preprocessing directives in typedefs
#if defined(__GNUC__) && __GNUC__ >= 4
    #define DEPRECATED __attribute__((deprecated))
#else
    #define DEPRECATED
#endif

// Nested struct with function pointer
typedef struct {
    int id;
    char name[64];
    int (*process_func)(int, char*);
    void (*cleanup_func)(void*);
} processor_t;

// Array of function pointers - nasty parsing edge case
typedef int (*math_operation_t)(int, int);
typedef math_operation_t math_ops_array_t[10];

// Function pointer returning function pointer
typedef int (*(*complex_func_ptr_t)(int, char*))(double, void*);

// Nested typedefs with function pointers
typedef struct {
    int value;
    char* name;
} data_item_t;

typedef int (*data_processor_t)(data_item_t* item, void* context);
typedef data_processor_t* data_processor_array_t;

// Union with function pointers
typedef union {
    int int_val;
    char* str_val;
    void (*void_func)(void);
    int (*int_func)(int);
} mixed_union_t;

// Struct with array of function pointers
typedef struct {
    int count;
    math_operation_t operations[5];
    void (*callbacks[3])(int, char*);
} operation_set_t;

// Complex nested struct with multiple function pointers
typedef struct {
    int id;
    struct {
        char name[32];
        int (*validate_func)(const char*);
        void (*format_func)(char*, int);
    } validator;
    struct {
        int max_size;
        void* (*alloc_func)(size_t);
        void (*free_func)(void*);
        int (*resize_func)(void**, size_t);
    } memory_manager;
} complex_handler_t;

// Enum with function pointer fields (simulated)
typedef enum {
    OP_ADD = 0,
    OP_SUB = 1,
    OP_MUL = 2,
    OP_DIV = 3
} operation_type_t;

// Function pointer typedef with complex parameters
typedef int (*complex_callback_t)(
    int param1,
    char* param2,
    void* param3,
    struct {
        int nested1;
        char* nested2;
        void (*nested_func)(int);
    }* param4
);

// Array of structs containing function pointers
typedef struct {
    int id;
    char name[16];
    void (*init_func)(void);
    int (*process_func)(int, int);
    void (*cleanup_func)(void);
} handler_entry_t;

typedef handler_entry_t handler_table_t[8];

// Preprocessing in function pointer typedefs
#if defined(DEBUG_MODE)
    typedef void (*debug_callback_t)(const char* message, int level);
#else
    typedef void (*release_callback_t)(const char* message);
#endif

// Nasty edge case: Complex typedef with const array of function pointers
typedef enum {
    PROCESSOR_CFG_MODULE_COUNT = 3,
    PROCESSOR_CFG_MODULE_ADAPTER = 0,
    PROCESSOR_CFG_MODULE_SERVICE = 1,
    PROCESSOR_CFG_MODULE_HARDWARE = 2
} processor_module_enum_t;

typedef struct {
    int job_id;
    char* job_data;
    size_t data_size;
    int priority;
} Process_T;

typedef int Std_ReturnType;

// The nasty edge case: const array of function pointers with complex name
typedef Std_ReturnType (*Process_Cfg_Process_fct)(const Process_T *job_pst);
typedef Process_Cfg_Process_fct Process_Cfg_Process_acpfct_t[PROCESSOR_CFG_MODULE_COUNT];

// Complex macro function with multiple parameters and nested logic
#define HANDLE_OPERATION(op_type, data, size, callback) do { \
    switch ((op_type)) { \
        case OP_ADD: \
            for (int i = 0; i < (size); i++) { \
                (data)[i] = (data)[i] + 1; \
            } \
            break; \
        case OP_SUB: \
            for (int i = 0; i < (size); i++) { \
                (data)[i] = (data)[i] - 1; \
            } \
            break; \
        case OP_MUL: \
            for (int i = 0; i < (size); i++) { \
                (data)[i] = (data)[i] * 2; \
            } \
            break; \
        case OP_DIV: \
            for (int i = 0; i < (size); i++) { \
                (data)[i] = (data)[i] / 2; \
            } \
            break; \
    } \
    if ((callback) != NULL) { \
        (callback)((data), (size)); \
    } \
} while(0)

// Function declarations with complex function pointer parameters
int process_with_callbacks(
    int data[],
    int size,
    math_operation_t operations[],
    int op_count,
    void (*pre_process)(int*, int),
    void (*post_process)(int*, int)
);

void* create_handler(
    const char* name,
    int (*init_func)(void*),
    void (*cleanup_func)(void*),
    complex_callback_t callback
);

// Array of function pointers as parameter
int execute_operations(
    int value,
    math_ops_array_t ops,
    int op_count
);

// Function returning array of function pointers
math_operation_t* get_math_operations(void);

// Complex function with nested struct and function pointers
complex_handler_t* create_complex_handler(
    const char* name,
    int (*validate_func)(const char*),
    void* (*alloc_func)(size_t),
    void (*free_func)(void*)
);

// Function declarations for the nasty edge case
void test_processor_job_processing(void);
void test_processor_utility_macros(void);

// ===================================================================
// COMPREHENSIVE ANONYMOUS TYPEDEF TEST CASES
// ===================================================================

// Case 1: struct-within-struct typedef
typedef struct {
    int outer_id;
    char outer_name[32];
    struct {
        int inner_x;
        int inner_y;
        char inner_label[16];
    } inner_struct;
    int outer_flags;
} struct_with_struct_t;

// Case 2: union-within-struct typedef  
typedef struct {
    int type_id;
    union {
        int int_value;
        float float_value;
        char string_value[64];
        struct {
            int x, y, z;
        } point_value;
    } data_union;
    int checksum;
} struct_with_union_t;

// Case 3: struct-within-union typedef
typedef union {
    int simple_int;
    float simple_float;
    struct {
        char header[16];
        int payload_size;
        void* payload_data;
        struct {
            int error_code;
            char error_msg[128];
        } error_info;
    } complex_struct;
    char raw_bytes[256];
} union_with_struct_t;

// Case 4: union-within-union typedef (nested unions)
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

// Case 5: Multiple anonymous structures in same typedef
typedef struct {
    struct {
        int first_x;
        int first_y;
    } first_anon_struct;
    union {
        int union_int;
        float union_float;
    } first_anon_union;
    struct {
        char second_name[32];
        int second_id;
        struct {
            int deep_value;
        } deep_struct;
    } second_anon_struct;
} multi_anonymous_t;

// Case 5b: Extended multiple anonymous - testing complex naming indexing
typedef struct {
    // First level - multiple structs
    struct {
        int first_a;
        struct {
            int nested_a1;
            struct {
                int deep_a1;
            } deep_struct_a1;
            struct {
                int deep_a2;
            } deep_struct_a2;
        } nested_struct_a;
        struct {
            int nested_a2;
        } nested_struct_a2;
    } first_struct;
    
    struct {
        int second_a;
        struct {
            int nested_b1;
        } nested_struct_b;
    } second_struct;
    
    // Mixed unions and structs
    union {
        int union_value;
        struct {
            int union_struct_field;
            struct {
                int deep_union_struct;
            } deep_in_union;
        } union_struct;
    } mixed_union;
    
    struct {
        int third_a;
        union {
            int struct_union_int;
            struct {
                int struct_union_struct_field;
            } struct_union_struct;
        } struct_union;
    } third_struct;
} complex_naming_test_t;

// Case 5c: Even more complex nesting to test indexing limits
typedef struct {
    struct {
        struct {
            struct {
                int level4_field;
            } level4_struct_1;
            struct {
                int level4_field2;
            } level4_struct_2;
        } level3_struct_1;
        struct {
            int level3_field;
        } level3_struct_2;
    } level2_struct_1;
    
    struct {
        union {
            struct {
                int mixed_field;
            } mixed_struct;
        } mixed_union;
    } level2_struct_2;
} extreme_nesting_test_t;

// Case 5d: Simple multiple anonymous to specifically test naming indexing
typedef struct {
    struct {
        int first_field;
    } first_anon;
    
    struct {
        int second_field;
    } second_anon;
    
    struct {
        int third_field;
    } third_anon;
    
    union {
        int union_field1;
    } first_union;
    
    union {
        int union_field2;
    } second_union;
} multiple_simple_anonymous_t;

// Case 6: Function pointer with anonymous struct parameter (already exists but let's add more)
typedef void (*callback_with_anon_struct_t)(
    int id,
    struct {
        int config_flags;
        char config_name[64];
        union {
            int int_config;
            float float_config;
        } config_value;
    }* config_param,
    void* user_data
);

// Case 7: Function pointer returning anonymous struct
typedef struct {
    int result_code;
    union {
        int success_value;
        char error_message[128];
    } result_data;
} (*result_generator_t)(int input_id, const char* input_name);

// Case 8: Array of anonymous structs
typedef struct {
    int count;
    struct {
        int item_id;
        char item_name[32];
        union {
            int int_data;
            float float_data;
            struct {
                int x, y;
            } point_data;
        } item_value;
    } items[10];
} array_of_anon_structs_t;

// Case 9: Moderately nested anonymous structures
typedef struct {
    int level1_id;
    struct {
        int level2_id;
        union {
            int level3_int;
            float level3_float;
        } level3_union;
    } level2_struct;
} moderately_nested_t;

// Case 10: Simple struct with standard fields
typedef struct {
    int event_count;
    char event_name[32];
    int event_flags;
} simplified_handler_t;

// The nasty const array of function pointers is defined in complex.c

#endif /* COMPLEX_H */