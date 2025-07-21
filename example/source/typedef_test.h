#ifndef TYPEDEF_TEST_H
#define TYPEDEF_TEST_H

#include <stdint.h>
#include "sample.h"
#include "config.h"
#include "logger.h"

// Basic type aliases
typedef uint32_t MyLen;
typedef int32_t MyInt;
typedef char* MyString;

// Struct definition
typedef struct {
    MyLen length;
    MyString data;
} MyBuffer;

// Function pointer typedef
typedef int (*MyCallback)(MyBuffer* buffer);

// Complex type definition
typedef struct MyComplexStruct {
    MyLen id;
    MyString name;
    MyCallback callback;
    log_level_t log_level; // New: use logger typedef
} MyComplex;

typedef MyComplex* MyComplexPtr;

// Enum typedef (anonymous)
typedef enum {
    COLOR_RED,
    COLOR_GREEN,
    COLOR_BLUE
} Color_t;

enum StatusEnum { STATUS_OK, STATUS_FAIL };
typedef enum StatusEnum Status_t;

typedef struct {
    int x;
    int y;
} Point_t;

struct NamedStruct { int a; int b; };
typedef struct NamedStruct NamedStruct_t;

typedef union {
    int i;
    float f;
} Number_t;

union NamedUnion { char c; double d; };
typedef union NamedUnion NamedUnion_t;

// New: Typedef for array of pointers
typedef MyComplexPtr MyComplexArray[10];

#endif // TYPEDEF_TEST_H