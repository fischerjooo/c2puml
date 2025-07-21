#ifndef MATH_UTILS_H
#define MATH_UTILS_H

#include "config.h"

// Typedefs
typedef double real_t;
typedef int (*math_op_t)(int, int);

// Function prototypes
int add(int a, int b);
int subtract(int a, int b);
real_t average(const int* arr, size_t len);

#endif // MATH_UTILS_H