#ifndef TYPEDEF_TEST_H
#define TYPEDEF_TEST_H

#include <stdint.h>
#include "sample.h"

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
} MyComplex;

// Another typedef that defines a new type
typedef MyComplex* MyComplexPtr;

// Enum typedef (anonymous)
typedef enum {
    COLOR_RED,
    COLOR_GREEN,
    COLOR_BLUE
} Color_t;

// Enum typedef (named)
enum StatusEnum { STATUS_OK, STATUS_FAIL };
typedef enum StatusEnum Status_t;

// Struct typedef (anonymous)
typedef struct {
    int x;
    int y;
} Point_t;

// Struct typedef (named)
struct NamedStruct { int a; int b; };
typedef struct NamedStruct NamedStruct_t;

// Union typedef (anonymous)
typedef union {
    int i;
    float f;
} Number_t;

// Union typedef (named)
union NamedUnion { char c; double d; };
typedef union NamedUnion NamedUnion_t;

#endif // TYPEDEF_TEST_H