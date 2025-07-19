#ifndef TYPES_H
#define TYPES_H

// Basic typedefs
typedef int MyInt;
typedef char* String;
typedef unsigned long ULong;

// Struct typedef
typedef struct {
    int x;
    int y;
} Point;

// Enum typedef
typedef enum {
    RED = 0,
    GREEN = 1,
    BLUE = 2
} Color;

// Union typedef
typedef union {
    int i;
    float f;
    char c;
} Value;

#endif // TYPES_H