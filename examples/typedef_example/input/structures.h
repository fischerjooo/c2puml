#ifndef STRUCTURES_H
#define STRUCTURES_H

#include "types.h"

// Struct using typedefs
struct ComplexStruct {
    Vector3D position;
    Color color;
    State state;
    Variant data;
    IntFunc callback;
};

typedef struct ComplexStruct ComplexStruct;
typedef ComplexStruct* ComplexStructPtr;

// Struct with nested typedefs
struct Container {
    Particle particles[100];
    NodePtr head;
    Direction direction;
    Data data;
    RGBColor rgb;
};

typedef struct Container Container;

// Union using typedefs
union FlexibleData {
    Integer integer;
    Float floating;
    String string;
    Pointer pointer;
    Variant variant;
};

typedef union FlexibleData FlexibleData;

// Enum using typedefs
enum Status {
    STATUS_OK = 0,
    STATUS_ERROR = 1,
    STATUS_WARNING = 2
};

typedef enum Status Status;

// Function using typedefs
IntFunc create_callback(IntFunc func);
VoidFunc create_void_callback(VoidFunc func);
StringFunc create_string_callback(StringFunc func);

// Global variables using typedefs
extern Integer global_integer;
extern String global_string;
extern Vector3D global_vector;
extern Color global_color;
extern State global_state;

#endif // STRUCTURES_H