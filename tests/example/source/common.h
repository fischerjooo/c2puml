#ifndef COMMON_H
#define COMMON_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

// Common error codes
#define SUCCESS 0
#define ERROR_GENERAL -1
#define ERROR_INVALID_PARAM -2
#define ERROR_MEMORY -3
#define ERROR_TIMEOUT -4

// Common types
typedef int32_t result_t;
typedef uint32_t id_t;
typedef bool status_bool_t;

// Common macros
#define UNUSED(x) (void)(x)
#define ARRAY_SIZE(arr) (sizeof(arr) / sizeof((arr)[0]))
#define MIN(a, b) ((a) < (b) ? (a) : (b))
#define MAX(a, b) ((a) > (b) ? (a) : (b))

// Common function attributes
#ifdef __GNUC__
#define DEPRECATED __attribute__((deprecated))
#define PACKED __attribute__((packed))
#else
#define DEPRECATED
#define PACKED
#endif

// Common status enum
typedef enum {
    STATUS_OK = 0,
    STATUS_ERROR = -1,
    STATUS_PENDING = 1,
    STATUS_TIMEOUT = 2
} common_status_t;

// Common utility functions
result_t common_init(void);
void common_cleanup(void);
const char* common_get_error_string(result_t error);

#endif // COMMON_H