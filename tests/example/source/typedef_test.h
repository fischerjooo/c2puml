#ifndef TYPEDEF_TEST_H
#define TYPEDEF_TEST_H

#include <stdint.h>
#include "sample.h"
#include "config.h"
#include "logger.h"

/* Basic type aliases */
typedef uint32_t MyLen;
typedef int32_t MyInt;
typedef char * MyString;

/* Struct definition with explicit tag */
typedef struct MyBuffer_tag {
    MyLen length;
    MyString data;
} MyBuffer;

/* Function pointer typedef for buffer callback */
typedef int (*MyCallback)(MyBuffer * buffer);

/* Complex type definition with explicit tag */
typedef struct MyComplexStruct_tag {
    MyLen id;
    MyString name;
    MyCallback callback;
    log_level_t log_level;
} MyComplex;

typedef MyComplex * MyComplexPtr;

/* Enum typedef with explicit tag */
typedef enum Color_tag {
    COLOR_RED = 0,
    COLOR_GREEN,
    COLOR_BLUE
} Color_t;

/* Status enum and typedef */
typedef enum StatusEnum_tag {
    STATUS_OK = 0,
    STATUS_FAIL
} Status_t;

/* Point struct with explicit tag */
typedef struct Point_tag {
    int x;
    int y;
} Point_t;

/* Named struct and typedef */
typedef struct NamedStruct_tag {
    int a;
    int b;
} NamedStruct_t;

/* Union typedef with explicit tag */
typedef union Number_tag {
    int i;
    float f;
} Number_t;

/* Named union and typedef */
typedef union NamedUnion_tag {
    char c;
    double d;
} NamedUnion_t;

/* Typedef for array of pointers */
typedef MyComplexPtr MyComplexArray[10];

/* Struct with multi-dimensional array sizes using U suffix */
typedef struct ArrayHolder_tag {
    int type_tst;
    int array_ofarray_aast[2U][2U];
} ArrayHolder_t;

#endif /* TYPEDEF_TEST_H */