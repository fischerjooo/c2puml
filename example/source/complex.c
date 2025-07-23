#include "complex.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Global array of function pointers - nasty parsing edge case
static math_operation_t global_math_ops[10] = {NULL};

// Nasty edge case: const array of function pointers with complex name
static Std_ReturnType rba_ProcessorAdapter_Process(const Process_T *job_pst) {
    if (job_pst == NULL) return -1;
    printf("Processing job %d with Adapter module\n", job_pst->job_id);
    return 0;
}

static Std_ReturnType rba_ProcessorService_Process(const Process_T *job_pst) {
    if (job_pst == NULL) return -1;
    printf("Processing job %d with Service module\n", job_pst->job_id);
    return 0;
}

static Std_ReturnType rba_ProcessorHardware_Process(const Process_T *job_pst) {
    if (job_pst == NULL) return -1;
    printf("Processing job %d with Hardware module\n", job_pst->job_id);
    return 0;
}

// The nasty edge case: const array of function pointers with complex name
Process_Cfg_Process_acpfct_t Process_Cfg_Process_acpfct = {
    &rba_ProcessorAdapter_Process,
    &rba_ProcessorService_Process,
    &rba_ProcessorHardware_Process,
};

// Static function implementations for math operations
static int add_operation(int a, int b) {
    return a + b;
}

static int subtract_operation(int a, int b) {
    return a - b;
}

static int multiply_operation(int a, int b) {
    return a * b;
}

static int divide_operation(int a, int b) {
    return (b != 0) ? a / b : 0;
}

static int modulo_operation(int a, int b) {
    return (b != 0) ? a % b : 0;
}

// Initialize global function pointer array
static void init_math_operations(void) {
    global_math_ops[0] = add_operation;
    global_math_ops[1] = subtract_operation;
    global_math_ops[2] = multiply_operation;
    global_math_ops[3] = divide_operation;
    global_math_ops[4] = modulo_operation;
    // Rest are NULL
}

// Function using the nasty multiline macro
void test_complex_macro(int* x, int y, int z) {
    COMPLEX_MACRO_FUNC(*x, y, z);
}

// Function using array processing macro
static int test_callback(int* item) {
    if (item == NULL) return -1;
    *item = *item * 2;
    return 0;
}

void test_process_array(int* arr, int size) {
    PROCESS_ARRAY(arr, size, test_callback);
}

// Function using complex macro with stringification
void test_stringify_macro(void) {
    int value = 42;
    printf("Value: %s = %d\n", TOSTRING(value), value);
}

// Function testing the nasty processor utility macros
void test_processor_utility_macros(void) {
    printf("=== Testing Processor Utility Macros (Nasty Edge Cases) ===\n");
    
    // Test uint16 to uint8 array conversion
    uint16 test_value_16 = 0x1234;
    uint8 buffer_16[2];
    
    UTILS_U16_TO_U8ARR_BIG_ENDIAN(test_value_16, buffer_16);
    printf("U16 0x%04X -> U8 array: [0x%02X, 0x%02X]\n", 
           test_value_16, buffer_16[0], buffer_16[1]);
    
    // Test uint32 to uint8 array conversion
    uint32 test_value_32 = 0x12345678;
    uint8 buffer_32[4];
    
    UTILS_U32_TO_U8ARR_BIG_ENDIAN(test_value_32, buffer_32);
    printf("U32 0x%08X -> U8 array: [0x%02X, 0x%02X, 0x%02X, 0x%02X]\n", 
           test_value_32, buffer_32[0], buffer_32[1], buffer_32[2], buffer_32[3]);
    
    // Test uint8 array to uint16 conversion
    uint16 converted_16 = UTILS_U8ARR_TO_U16_BIG_ENDIAN(buffer_16);
    printf("U8 array [0x%02X, 0x%02X] -> U16: 0x%04X\n", 
           buffer_16[0], buffer_16[1], converted_16);
    
    // Test uint8 array to uint32 conversion
    uint32 converted_32 = UTILS_U8ARR_TO_U32_BIG_ENDIAN(buffer_32);
    printf("U8 array [0x%02X, 0x%02X, 0x%02X, 0x%02X] -> U32: 0x%08X\n", 
           buffer_32[0], buffer_32[1], buffer_32[2], buffer_32[3], converted_32);
    
    // Test with different values
    uint16 test_value_16_2 = 0xABCD;
    uint8 buffer_16_2[2];
    UTILS_U16_TO_U8ARR_BIG_ENDIAN(test_value_16_2, buffer_16_2);
    printf("U16 0x%04X -> U8 array: [0x%02X, 0x%02X]\n", 
           test_value_16_2, buffer_16_2[0], buffer_16_2[1]);
    
    printf("=== Processor Utility Macros Test Complete ===\n");
}

// Static callback function for operation handling
static void print_result(int* data, int size) {
    printf("Result: ");
    for (int i = 0; i < size; i++) {
        printf("%d ", data[i]);
    }
    printf("\n");
}

// Function using the operation handling macro
void test_handle_operation(operation_type_t op_type, int* data, int size) {
    void (*callback)(int*, int) = NULL;
    
    callback = print_result;
    HANDLE_OPERATION(op_type, data, size, callback);
}

// Implementation of process_with_callbacks with complex function pointer usage
int process_with_callbacks(
    int data[],
    int size,
    math_operation_t operations[],
    int op_count,
    void (*pre_process)(int*, int),
    void (*post_process)(int*, int)
) {
    if (data == NULL || operations == NULL) {
        return -1;
    }
    
    // Use pre-processing callback if provided
    if (pre_process != NULL) {
        pre_process(data, size);
    }
    
    // Apply operations using function pointer array
    for (int i = 0; i < op_count && i < size; i++) {
        if (operations[i] != NULL) {
            data[i] = operations[i](data[i], i + 1);
        }
    }
    
    // Use post-processing callback if provided
    if (post_process != NULL) {
        post_process(data, size);
    }
    
    return 0;
}

// Implementation using complex function pointer typedef
void* create_handler(
    const char* name,
    int (*init_func)(void*),
    void (*cleanup_func)(void*),
    complex_callback_t callback
) {
    processor_t* handler = malloc(sizeof(processor_t));
    if (handler == NULL) {
        return NULL;
    }
    
    handler->id = 1;
    strncpy(handler->name, name, sizeof(handler->name) - 1);
    handler->name[sizeof(handler->name) - 1] = '\0';
    handler->process_func = NULL; // Will be set later
    handler->cleanup_func = cleanup_func;
    
    // Call init function if provided
    if (init_func != NULL) {
        int result = init_func(handler);
        if (result != 0) {
            if (cleanup_func != NULL) {
                cleanup_func(handler);
            }
            free(handler);
            return NULL;
        }
    }
    
    return handler;
}

// Implementation using array of function pointers
int execute_operations(int value, math_ops_array_t ops, int op_count) {
    int result = value;
    
    for (int i = 0; i < op_count && i < 10; i++) {
        if (ops[i] != NULL) {
            result = ops[i](result, i + 1);
        }
    }
    
    return result;
}

// Function returning array of function pointers
math_operation_t* get_math_operations(void) {
    static int initialized = 0;
    
    if (!initialized) {
        init_math_operations();
        initialized = 1;
    }
    
    return global_math_ops;
}

// Complex function with nested struct and function pointers
complex_handler_t* create_complex_handler(
    const char* name,
    int (*validate_func)(const char*),
    void* (*alloc_func)(size_t),
    void (*free_func)(void*)
) {
    complex_handler_t* handler = malloc(sizeof(complex_handler_t));
    if (handler == NULL) {
        return NULL;
    }
    
    handler->id = 1;
    strncpy(handler->validator.name, name, sizeof(handler->validator.name) - 1);
    handler->validator.name[sizeof(handler->validator.name) - 1] = '\0';
    handler->validator.validate_func = validate_func;
    handler->validator.format_func = NULL;
    
    handler->memory_manager.max_size = 1024;
    handler->memory_manager.alloc_func = alloc_func ? alloc_func : malloc;
    handler->memory_manager.free_func = free_func ? free_func : free;
    handler->memory_manager.resize_func = NULL;
    
    return handler;
}

// Function demonstrating union with function pointers
void test_mixed_union(void) {
    mixed_union_t mixed;
    
    // Set function pointer
    mixed.void_func = (void (*)(void))printf;
    
    // Call function through union
    if (mixed.void_func != NULL) {
        ((void (*)(const char*))mixed.void_func)("Testing union function pointer\n");
    }
}

// Function demonstrating struct with array of function pointers
void test_operation_set(void) {
    operation_set_t ops_set;
    ops_set.count = 3;
    
    // Initialize function pointer array
    ops_set.operations[0] = add_operation;
    ops_set.operations[1] = multiply_operation;
    ops_set.operations[2] = subtract_operation;
    
    // Test operations
    int result = 10;
    for (int i = 0; i < ops_set.count; i++) {
        if (ops_set.operations[i] != NULL) {
            result = ops_set.operations[i](result, i + 1);
        }
    }
    
    printf("Operation set result: %d\n", result);
}

// Function demonstrating handler table usage
void test_handler_table(void) {
    handler_table_t table = {0};
    
    // Initialize some entries
    table[0].id = 1;
    strcpy(table[0].name, "Handler1");
    table[0].init_func = (void (*)(void))printf;
    table[0].process_func = add_operation;
    table[0].cleanup_func = (void (*)(void))printf;
    
    // Use the handler
    if (table[0].init_func != NULL) {
        table[0].init_func();
    }
    
    if (table[0].process_func != NULL) {
        int result = table[0].process_func(5, 42);
        printf("Handler result: %d\n", result);
    }
}

// Function demonstrating the nasty edge case: const array of function pointers
void test_processor_job_processing(void) {
    printf("=== Testing Processor Job Processing (Nasty Edge Case) ===\n");
    
    // Create test jobs
    Process_T jobs[PROCESSOR_CFG_MODULE_COUNT] = {
        {1, "Adapter_Data", 10, 1},
        {2, "Service_Data", 15, 2},
        {3, "Hardware_Data", 20, 3}
    };
    
    // Process jobs using the nasty const array of function pointers
    for (int i = 0; i < PROCESSOR_CFG_MODULE_COUNT; i++) {
        if (Process_Cfg_Process_acpfct[i] != NULL) {
            Std_ReturnType result = Process_Cfg_Process_acpfct[i](&jobs[i]);
            printf("Job %d processing result: %d\n", i + 1, result);
        }
    }
    
    // Test with NULL job
    if (Process_Cfg_Process_acpfct[0] != NULL) {
        Std_ReturnType result = Process_Cfg_Process_acpfct[0](NULL);
        printf("NULL job processing result: %d\n", result);
    }
    
    printf("=== Processor Job Processing Test Complete ===\n");
}

// Main test function that exercises all the nasty parsing edge cases
void run_complex_tests(void) {
    printf("=== Complex Parsing Edge Cases Test ===\n");
    
    // Test complex macro
    int x = 10;
    test_complex_macro(&x, 5, 3);
    printf("Complex macro result: %d\n", x);
    
    // Test array processing macro
    int arr[] = {1, 2, 3, 4, 5};
    test_process_array(arr, 5);
    printf("Array processing result: ");
    for (int i = 0; i < 5; i++) {
        printf("%d ", arr[i]);
    }
    printf("\n");
    
    // Test stringify macro
    test_stringify_macro();
    
    // Test operation handling macro
    int data[] = {10, 20, 30, 40, 50};
    test_handle_operation(OP_ADD, data, 5);
    
    // Test function pointer array
    math_ops_array_t local_ops = {add_operation, multiply_operation, subtract_operation};
    int result = execute_operations(10, local_ops, 3);
    printf("Function pointer array result: %d\n", result);
    
    // Test mixed union
    test_mixed_union();
    
    // Test operation set
    test_operation_set();
    
    // Test handler table
    test_handler_table();
    
    // Test the nasty edge case: const array of function pointers
    test_processor_job_processing();
    
    // Test the nasty processor utility macros
    test_processor_utility_macros();
    
    printf("=== Complex Tests Complete ===\n");
}