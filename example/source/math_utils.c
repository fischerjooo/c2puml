#include "math_utils.h"

int add(int a, int b) {
    return a + b;
}

int subtract(int a, int b) {
    return a - b;
}

real_t average(const int* arr, size_t len) {
    if (!arr || len == 0) return 0.0;
    int sum = 0;
    for (size_t i = 0; i < len; ++i) sum += arr[i];
    return (real_t)sum / len;
}