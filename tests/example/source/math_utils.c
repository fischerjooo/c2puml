#include "math_utils.h"

int add(int a, int b)
{
    return a + b;
}

int subtract(int a, int b)
{
    return a - b;
}

real_t average(const int * arr, size_t len)
{
    if ((arr == NULL) || (len == 0U))
    {
        return 0.0;
    }
    int sum = 0;
    size_t i;
    for (i = 0U; i < len; ++i)
    {
        sum += arr[i];
    }
    return (real_t)sum / (real_t)len;
}