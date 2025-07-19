#ifndef UTILS_H
#define UTILS_H

#include "core.h"

// Utility structures
typedef struct {
    int x, y, z;
} Vector3D;

typedef union {
    int i;
    float f;
    char* s;
} Variant;

typedef enum {
    UTIL_SUCCESS = 0,
    UTIL_FAILURE = 1
} UtilResult;

// Utility functions
uint32_t generate_id(void);
UtilResult validate_string(const char* str);
Vector3D* create_vector(int x, int y, int z);
void destroy_vector(Vector3D* vec);
Variant* create_variant(void);
void destroy_variant(Variant* var);

// Macros
#define UTIL_MAX(a, b) ((a) > (b) ? (a) : (b))
#define UTIL_MIN(a, b) ((a) < (b) ? (a) : (b))

// Global variables
extern int util_debug_level;
extern char* util_error_message;

#endif // UTILS_H