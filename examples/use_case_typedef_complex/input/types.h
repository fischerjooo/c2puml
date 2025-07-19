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

// Anonymous union typedefs
typedef union {
    int i;
    float f;
    char c;
    void* ptr;
} Variant;

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

#endif