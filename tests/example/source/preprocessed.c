#include "preprocessed.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Test preprocessing directives in function implementations
#if FEATURE_ENABLED
int process_feature(enabled_feature_t* feature) {
    if (!feature) return -1;
    
    #if DEBUG_MODE
        printf("Debug: Processing feature with ID %d\n", feature->id);
    #endif
    
    feature->id++;
    strcpy(feature->name, "processed");
    return 0;
}

#if DEBUG_MODE
void debug_feature(enabled_feature_t* feature) {
    printf("Debug feature - ID: %d, Name: %s\n", feature->id, feature->name);
}
#endif

#else
int process_basic(void) {
    #if DEBUG_MODE
        printf("Debug: Processing basic functionality\n");
    #endif
    return 0;
}
#endif

// Global variables with preprocessing
#if FEATURE_ENABLED
enabled_feature_t global_feature = {0, ""};

#if DEBUG_MODE
debug_struct_t global_debug = {0, "", 0};
#endif

#else
int global_basic = 0;
#endif

// Function with nested preprocessing
void complex_function(void) {
    #if FEATURE_ENABLED
        #if DEBUG_MODE
            printf("Debug mode with features enabled\n");
            #if MAX_SIZE > 50
                printf("Using large buffer size: %d\n", MAX_SIZE);
            #else
                printf("Using small buffer size: %d\n", MIN_SIZE);
            #endif
        #else
            printf("Release mode with features enabled\n");
        #endif
    #else
        printf("Features disabled\n");
    #endif
}

// Test function for preprocessing edge cases
void test_preprocessing_edge_cases(void) {
    // Test conditional compilation in variable declarations
    #if FEATURE_ENABLED
        enabled_feature_t local_feature = {1, "test"};
        #if DEBUG_MODE
            debug_struct_t local_debug = {2, "debug_test", 42};
        #endif
    #else
        int local_basic = 42;
    #endif
    
    // Test preprocessing in switch statements
    status_t status = STATUS_ENABLED;
    switch (status) {
        #if FEATURE_ENABLED
        case STATUS_ENABLED:
            printf("Status: Enabled\n");
            break;
        case STATUS_DISABLED:
            printf("Status: Disabled\n");
            break;
        #else
        case STATUS_OFF:
            printf("Status: Off\n");
            break;
        #endif
        case STATUS_UNKNOWN:
            printf("Status: Unknown\n");
            break;
        default:
            printf("Status: Default\n");
            break;
    }
    
    // Test preprocessing in array declarations
    #if MAX_SIZE > 50
        large_buffer_t buffer;
        strcpy(buffer, "large buffer test");
    #else
        small_buffer_t buffer;
        strcpy(buffer, "small buffer test");
    #endif
    
    printf("Buffer: %s\n", buffer);
}

// Function with preprocessing in typedef usage
void test_typedef_preprocessing(void) {
    #if FEATURE_ENABLED
        feature_struct_t feature = {1, "feature_test"};
        printf("Feature struct - ID: %d, Name: %s\n", feature.feature_id, feature.feature_name);
    #elif DEBUG_MODE
        debug_feature_t debug = {2, "debug_test"};
        printf("Debug feature - ID: %d, Name: %s\n", debug.debug_id, debug.debug_name);
    #else
        basic_struct_t basic = {3};
        printf("Basic struct - ID: %d\n", basic.basic_id);
    #endif
    
    // Test union with preprocessing
    #if FEATURE_ENABLED
        feature_union_t union_test;
        union_test.int_value = 42;
        printf("Union int value: %d\n", union_test.int_value);
        #if DEBUG_MODE
            union_test.debug_value = 3.14;
            printf("Union debug value: %f\n", union_test.debug_value);
        #endif
    #else
        basic_union_t basic_union;
        basic_union.int_value = 42;
        printf("Basic union int value: %d\n", basic_union.int_value);
    #endif
}

// Function with preprocessing in function pointers
void test_function_pointers(void) {
    #if FEATURE_ENABLED
        feature_callback_t callback = process_feature;
        enabled_feature_t test_feature = {1, "callback_test"};
        int result = callback(&test_feature);
        printf("Callback result: %d\n", result);
    #else
        basic_callback_t basic_callback = process_basic;
        int result = basic_callback();
        printf("Basic callback result: %d\n", result);
    #endif
}

// Main function with comprehensive preprocessing testing
int main(void) {
    printf("=== Preprocessing Test Program ===\n");
    
    // Test basic preprocessing
    complex_function();
    
    // Test edge cases
    test_preprocessing_edge_cases();
    
    // Test typedef preprocessing
    test_typedef_preprocessing();
    
    // Test function pointers
    test_function_pointers();
    
    // Test global variables
    #if FEATURE_ENABLED
        printf("Global feature ID: %d\n", global_feature.id);
        #if DEBUG_MODE
            printf("Global debug ID: %d\n", global_debug.debug_id);
        #endif
    #else
        printf("Global basic: %d\n", global_basic);
    #endif
    
    printf("=== Test completed ===\n");
    return 0;
}