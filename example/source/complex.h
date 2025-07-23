#ifndef COMPLEX_H
#define COMPLEX_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

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
        if ((arr)[i] != NULL) { \
            int result = (callback)((arr)[i]); \
            if (result < 0) { \
                break; \
            } \
        } \
    } \
} while(0)

// Complex macro with stringification and concatenation
#define CREATE_FUNC_NAME(prefix, suffix) prefix##_##suffix
#define STRINGIFY(x) #x
#define TOSTRING(x) STRINGIFY(x)

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
    int (*process_func)(int, char*);
    void (*cleanup_func)(void);
} handler_entry_t;

typedef handler_entry_t handler_table_t[8];

// Preprocessing in function pointer typedefs
#if defined(DEBUG_MODE)
    typedef void (*debug_callback_t)(const char* message, int level);
#else
    typedef void (*release_callback_t)(const char* message);
#endif

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

#endif /* COMPLEX_H */