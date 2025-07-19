#ifndef TYPES_H
#define TYPES_H

typedef int MyInt;
typedef char* String;
typedef unsigned long ULong;

typedef struct {
    int x;
    int y;
} Point;

typedef enum {
    RED = 0,
    GREEN = 1,
    BLUE = 2
} Color;

typedef union {
    int i;
    float f;
    char c;
} Value;

#endif