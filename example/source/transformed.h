#ifndef TRANSFORMED_H
#define TRANSFORMED_H

#include <stdio.h>

// Legacy includes that can be removed
#include <time.h>
#include <unistd.h>

// Legacy typedefs that can be removed/renamed
typedef unsigned int legacy_uint_t;
typedef void* legacy_handle_t;
typedef struct old_config old_config_t;

// Deprecated macros that can be removed
#define LEGACY_BUFFER_SIZE 512
#define OLD_API_VERSION 100
#define DEPRECATED_FLAG 0x01

// Global variable declarations that can be removed/renamed
extern int old_error_code;
extern char* legacy_path;

// Deprecated structure declarations that can be removed/renamed
struct old_config {
    int version;
    char name[64];
    int flags;
};

struct legacy_node {
    int data;
    struct legacy_node* next;
};

// Deprecated enum declarations that can be removed/renamed
enum old_error_type {
    OLD_ERROR_NONE,
    OLD_ERROR_INVALID,
    OLD_ERROR_MEMORY
};

enum legacy_mode {
    LEGACY_MODE_READ,
    LEGACY_MODE_WRITE,
    LEGACY_MODE_APPEND
};

// Deprecated union declarations that can be removed/renamed
union old_variant {
    int int_val;
    double double_val;
    char* string_val;
};

// Legacy function declarations that can be removed/renamed
int legacy_init(old_config_t* config);
void deprecated_cleanup(void);
old_config_t* old_create_config(const char* name);

// Test function declarations that can be removed
void test_helper_function(void);
int debug_validate_config(old_config_t* config);

// Function declarations that should remain after transformations
int main(void);
void keep_this_function(void);

// New style declarations that should remain
typedef struct {
    int x;
    int y;
    int z;
} point3d_t;

typedef enum {
    STATUS_OK,
    STATUS_ERROR,
    STATUS_PENDING
} status_t;

// Modern function declarations
status_t initialize_system(void);
void process_data(const point3d_t* point);
void cleanup_resources(void);

#endif // TRANSFORMED_H