#include "core.h"
#include "utils.h"
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char* argv[]) {
    CoreStatus status;
    CoreObject* obj;
    Vector3D* vec;
    Variant* var;
    
    // Initialize core
    status = core_init();
    if (status != CORE_OK) {
        fprintf(stderr, "Failed to initialize core\n");
        return 1;
    }
    
    // Create objects
    obj = core_create_object("test_object");
    if (!obj) {
        fprintf(stderr, "Failed to create object\n");
        core_cleanup();
        return 1;
    }
    
    vec = create_vector(1, 2, 3);
    if (!vec) {
        fprintf(stderr, "Failed to create vector\n");
        core_destroy_object(obj);
        core_cleanup();
        return 1;
    }
    
    var = create_variant();
    if (!var) {
        fprintf(stderr, "Failed to create variant\n");
        destroy_vector(vec);
        core_destroy_object(obj);
        core_cleanup();
        return 1;
    }
    
    // Use objects
    printf("Object ID: %u, Name: %s\n", obj->id, obj->name);
    printf("Vector: (%d, %d, %d)\n", vec->x, vec->y, vec->z);
    printf("Variant value: %d\n", var->i);
    
    // Cleanup
    destroy_variant(var);
    destroy_vector(vec);
    core_destroy_object(obj);
    core_cleanup();
    
    return 0;
}