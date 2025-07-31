#ifndef PREPROCESSED_H
#define PREPROCESSED_H

#include <stdint.h>
#include <stddef.h>

// Basic preprocessing directives
#define FEATURE_ENABLED 1
#define DEBUG_MODE 0
#define MAX_SIZE 100
#define MIN_SIZE 10

// Conditional compilation in typedefs
#if FEATURE_ENABLED
typedef struct {
    int id;
    char name[32];
} enabled_feature_t;
#else
typedef struct {
    int id;
} disabled_feature_t;
#endif

// Nested preprocessing in typedefs
#if DEBUG_MODE
    #if MAX_SIZE > 50
        typedef struct {
            int debug_id;
            char debug_name[64];
            #if MIN_SIZE < 20
                int extra_debug_field;
            #endif
        } debug_struct_t;
    #else
        typedef struct {
            int debug_id;
        } simple_debug_t;
    #endif
#else
    typedef struct {
        int release_id;
    } release_struct_t;
#endif

// Preprocessing in enum typedefs
typedef enum {
    #if FEATURE_ENABLED
        STATUS_ENABLED = 1,
        STATUS_DISABLED = 0,
    #else
        STATUS_OFF = 0,
    #endif
    STATUS_UNKNOWN = -1
} status_t;

// Complex preprocessing with multiple conditions
#if defined(FEATURE_ENABLED) && !defined(DEBUG_MODE)
    typedef struct {
        int optimized_field;
        #if MAX_SIZE > 50
            char large_buffer[MAX_SIZE];
        #else
            char small_buffer[MIN_SIZE];
        #endif
    } optimized_struct_t;
#elif defined(DEBUG_MODE)
    typedef struct {
        int debug_field;
        char debug_buffer[128];
    } debug_optimized_t;
#else
    typedef struct {
        int default_field;
    } default_struct_t;
#endif

// Preprocessing in function pointer typedefs
#if FEATURE_ENABLED
    typedef int (*feature_callback_t)(enabled_feature_t* feature);
#else
    typedef int (*basic_callback_t)(void);
#endif

// Preprocessing in array typedefs
#if MAX_SIZE > 50
    typedef char large_buffer_t[MAX_SIZE];
#else
    typedef char small_buffer_t[MIN_SIZE];
#endif

// Nested #ifdef in typedefs
#ifdef FEATURE_ENABLED
    #ifdef DEBUG_MODE
        typedef struct {
            int debug_enabled_id;
            char debug_enabled_name[64];
        } debug_enabled_t;
    #else
        typedef struct {
            int enabled_id;
            char enabled_name[32];
        } enabled_t;
    #endif
#else
    typedef struct {
        int disabled_id;
    } disabled_t;
#endif

// Preprocessing with #elif
#if FEATURE_ENABLED
    typedef struct {
        int feature_id;
        char feature_name[32];
    } feature_struct_t;
#elif DEBUG_MODE
    typedef struct {
        int debug_id;
        char debug_name[64];
    } debug_feature_t;
#else
    typedef struct {
        int basic_id;
    } basic_struct_t;
#endif

// Preprocessing in union typedefs
#if FEATURE_ENABLED
    typedef union {
        int int_value;
        char char_value;
        #if DEBUG_MODE
            double debug_value;
        #endif
    } feature_union_t;
#else
    typedef union {
        int int_value;
        char char_value;
    } basic_union_t;
#endif

// Function declarations with preprocessing
#if FEATURE_ENABLED
    int process_feature(enabled_feature_t* feature);
    #if DEBUG_MODE
        void debug_feature(enabled_feature_t* feature);
    #endif
#else
    int process_basic(void);
#endif

// Global variables with preprocessing
#if FEATURE_ENABLED
    extern enabled_feature_t global_feature;
    #if DEBUG_MODE
        extern debug_struct_t global_debug;
    #endif
#else
    extern int global_basic;
#endif

#endif // PREPROCESSED_H