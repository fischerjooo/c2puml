#ifndef MATH_UTILS_H
#define MATH_UTILS_H

#include "config.h"

/* Typedef for real number type */
typedef double real_t;

/* Function pointer typedef for math operations */
typedef int (*math_op_t)(int, int);

/* Function prototypes */
int add(int a, int b);
int subtract(int a, int b);
real_t average(const int * arr, size_t len);

#endif /* MATH_UTILS_H */