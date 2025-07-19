#include "core.h"
#include "utils.h"
#include <stdlib.h>
#include <string.h>

// Global variables
int core_initialized = 0;
CoreObject* core_default_object = NULL;

// Internal structures
struct CoreInternal {
    int magic;
    char* buffer;
    size_t buffer_size;
};

typedef struct CoreInternal CoreInternal;

// Internal functions
static CoreInternal* create_internal(void);
static void destroy_internal(CoreInternal* internal);

CoreStatus core_init(void) {
    if (core_initialized) {
        return CORE_ERROR;
    }
    
    core_default_object = core_create_object("default");
    if (!core_default_object) {
        return CORE_ERROR;
    }
    
    core_initialized = 1;
    return CORE_OK;
}

CoreStatus core_cleanup(void) {
    if (!core_initialized) {
        return CORE_ERROR;
    }
    
    if (core_default_object) {
        core_destroy_object(core_default_object);
        core_default_object = NULL;
    }
    
    core_initialized = 0;
    return CORE_OK;
}

CoreObject* core_create_object(const char* name) {
    CoreObject* obj = malloc(sizeof(CoreObject));
    if (!obj) {
        return NULL;
    }
    
    obj->id = generate_id();
    strncpy(obj->name, name ? name : "unnamed", sizeof(obj->name) - 1);
    obj->name[sizeof(obj->name) - 1] = '\0';
    obj->status = CORE_OK;
    
    return obj;
}

void core_destroy_object(CoreObject* obj) {
    if (obj) {
        free(obj);
    }
}