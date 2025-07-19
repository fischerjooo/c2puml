#include <stdio.h>
#include <stdlib.h>
#include "types.h"
#include "structures.h"

// Global variables using typedefs
Integer global_integer = 42;
String global_string = "Hello, Typedef World!";
Vector3D global_vector = {1, 2, 3};
Color global_color = {1.0, 0.5, 0.0, 1.0};
State global_state = STATE_RUNNING;

// Function implementations using typedefs
IntFunc create_callback(IntFunc func) {
    return func;
}

VoidFunc create_void_callback(VoidFunc func) {
    return func;
}

StringFunc create_string_callback(StringFunc func) {
    return func;
}

// Example functions using typedefs
Integer add_integers(Integer a, Integer b) {
    return a + b;
}

Float multiply_floats(Float a, Float b) {
    return a * b;
}

String create_string(const char* str) {
    return (String)str;
}

Vector3D create_vector(Integer x, Integer y, Integer z) {
    Vector3D v = {x, y, z};
    return v;
}

Color create_color(Float r, Float g, Float b, Float a) {
    Color c = {r, g, b, a};
    return c;
}

Variant create_variant(Integer type, void* data) {
    Variant v;
    switch (type) {
        case 0: v.i = *(Integer*)data; break;
        case 1: v.f = *(Float*)data; break;
        case 2: v.c = *(Character*)data; break;
        case 3: v.ptr = data; break;
    }
    return v;
}

int main() {
    // Using basic typedefs
    Integer x = 10;
    Float y = 3.14;
    String message = "Hello";
    
    // Using complex typedefs
    Vector3D pos = create_vector(1, 2, 3);
    Color col = create_color(1.0, 0.0, 0.0, 1.0);
    Variant var = create_variant(0, &x);
    
    // Using function pointer typedefs
    IntFunc add_func = add_integers;
    StringFunc str_func = create_string;
    
    // Using struct typedefs
    ComplexStruct cs = {
        .position = pos,
        .color = col,
        .state = STATE_RUNNING,
        .data = var,
        .callback = add_func
    };
    
    // Using union typedefs
    FlexibleData fd;
    fd.integer = 42;
    
    // Using enum typedefs
    State current_state = STATE_IDLE;
    ErrorCode error = ERROR_NONE;
    
    printf("Integer: %d\n", x);
    printf("Float: %f\n", y);
    printf("String: %s\n", message);
    printf("Vector: (%d, %d, %d)\n", pos.x, pos.y, pos.z);
    printf("Color: (%.2f, %.2f, %.2f, %.2f)\n", col.r, col.g, col.b, col.a);
    printf("State: %d\n", current_state);
    
    return 0;
}