#include "utils.h"
#include <stdlib.h>
#include <string.h>
#include <time.h>

// Global variables
int util_debug_level = 0;
char* util_error_message = NULL;

// Static variables
static uint32_t id_counter = 0;

uint32_t generate_id(void) {
    return ++id_counter;
}

UtilResult validate_string(const char* str) {
    if (!str) {
        return UTIL_FAILURE;
    }
    
    if (strlen(str) == 0) {
        return UTIL_FAILURE;
    }
    
    return UTIL_SUCCESS;
}

Vector3D* create_vector(int x, int y, int z) {
    Vector3D* vec = malloc(sizeof(Vector3D));
    if (!vec) {
        return NULL;
    }
    
    vec->x = x;
    vec->y = y;
    vec->z = z;
    
    return vec;
}

void destroy_vector(Vector3D* vec) {
    if (vec) {
        free(vec);
    }
}

Variant* create_variant(void) {
    Variant* var = malloc(sizeof(Variant));
    if (!var) {
        return NULL;
    }
    
    var->i = 0;
    return var;
}

void destroy_variant(Variant* var) {
    if (var) {
        if (var->s) {
            free(var->s);
        }
        free(var);
    }
}