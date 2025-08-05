#include "transformed.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Legacy typedefs that can be removed/renamed
typedef int legacy_int_t;
typedef char* legacy_string_t;
// Note: old_point_t is defined as void* in transformed.h, so we need to use the struct directly
struct old_point {
    int x;
    int y;
};

// Deprecated macros that can be removed
#define DEPRECATED_MAX_SIZE 1024
#define OLD_VERSION "1.0"
#define LEGACY_DEBUG 1

// Global variables that can be removed/renamed
int old_global_counter = 0;
legacy_string_t deprecated_message = "old version";

// Deprecated structures that can be removed/renamed
// old_point struct is now defined above

struct legacy_data {
    int id;
    char name[32];
    struct old_point position;
};

// Deprecated enums that can be removed/renamed
enum old_status {
    OLD_STATUS_PENDING,
    OLD_STATUS_ACTIVE,
    OLD_STATUS_INACTIVE
};

enum legacy_color {
    LEGACY_RED,
    LEGACY_GREEN,
    LEGACY_BLUE
};

// Deprecated unions that can be removed/renamed
union old_value {
    int i;
    float f;
    char c;
};

// Legacy functions that can be removed/renamed
int legacy_calculate(int a, int b) {
    return a + b + old_global_counter;
}

void deprecated_print_info(const char* message) {
    printf("DEPRECATED: %s\n", message);
}

struct old_point* old_create_point(int x, int y) {
    struct old_point* point = malloc(sizeof(struct old_point));
    if (point) {
        point->x = x;
        point->y = y;
    }
    return point;
}

// Test functions that can be removed
void test_function_one() {
    printf("Test function 1\n");
}

void test_function_two() {
    printf("Test function 2\n");
}

void debug_log(const char* msg) {
    #ifdef LEGACY_DEBUG
    printf("DEBUG: %s\n", msg);
    #endif
}

// Functions that should remain after transformations
int main() {
    printf("Main application\n");
    
    // Use some legacy functions (these calls would need updating after transformation)
    legacy_calculate(1, 2);
    deprecated_print_info("test message");
    
    struct old_point* pt = old_create_point(10, 20);
    if (pt) {
        printf("Point: (%d, %d)\n", pt->x, pt->y);
        free(pt);
    }
    
    return 0;
}

void keep_this_function() {
    printf("This function should remain\n");
}