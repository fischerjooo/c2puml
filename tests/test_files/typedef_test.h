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

#endif // TYPEDEF_TEST_H