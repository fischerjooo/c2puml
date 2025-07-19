#ifndef CORE_H
#define CORE_H

#include <stdint.h>

// Core data structures
typedef struct {
    uint32_t id;
    char name[64];
    int status;
} CoreObject;

typedef enum {
    CORE_OK = 0,
    CORE_ERROR = 1,
    CORE_INVALID = 2
} CoreStatus;

// Core functions
CoreStatus core_init(void);
CoreStatus core_cleanup(void);
CoreObject* core_create_object(const char* name);
void core_destroy_object(CoreObject* obj);

// Global variables
extern int core_initialized;
extern CoreObject* core_default_object;

#endif // CORE_H