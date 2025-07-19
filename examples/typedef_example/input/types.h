#ifndef TYPES_H
#define TYPES_H

// Basic type aliases
typedef int Integer;
typedef unsigned int UInteger;
typedef char Character;
typedef float Float;
typedef double Double;
typedef void* Pointer;

// Typedef chains
typedef Integer Int32;
typedef Int32 MyInt;
typedef MyInt Counter;

// Pointer typedefs
typedef int* IntPtr;
typedef char* String;
typedef void* VoidPtr;
typedef IntPtr* IntPtrPtr;

// Array typedefs
typedef int IntArray[10];
typedef char CharArray[256];
typedef float FloatArray[3];

// Function pointer typedefs
typedef int (*IntFunc)(int, int);
typedef void (*VoidFunc)(void);
typedef char* (*StringFunc)(const char*);

// Anonymous struct typedefs
typedef struct {
    int x;
    int y;
    int z;
} Vector3D;

typedef struct {
    float r;
    float g;
    float b;
    float a;
} Color;

// Anonymous enum typedefs
typedef enum {
    STATE_IDLE = 0,
    STATE_RUNNING = 1,
    STATE_PAUSED = 2,
    STATE_STOPPED = 3
} State;

typedef enum {
    ERROR_NONE = 0,
    ERROR_INVALID = -1,
    ERROR_TIMEOUT = -2,
    ERROR_MEMORY = -3
} ErrorCode;

// Anonymous union typedefs
typedef union {
    int i;
    float f;
    char c;
    void* ptr;
} Variant;

typedef union {
    struct {
        unsigned char r, g, b;
    } rgb;
    unsigned int value;
} RGBColor;

// Complex nested typedefs
typedef struct {
    Vector3D position;
    Vector3D velocity;
    float mass;
} Particle;

typedef Particle* ParticlePtr;
typedef ParticlePtr* ParticlePtrPtr;

// Typedef with struct tag
struct Node {
    int data;
    struct Node* next;
};
typedef struct Node Node;
typedef Node* NodePtr;

// Typedef with enum tag
enum Direction {
    DIR_NORTH,
    DIR_SOUTH,
    DIR_EAST,
    DIR_WEST
};
typedef enum Direction Direction;

// Typedef with union tag
union Data {
    int integer;
    float floating;
    char character;
};
typedef union Data Data;

#endif // TYPES_H