#ifndef UTILS_H
#define UTILS_H

#include <string.h>
#include "types.h"
#include "config.h"

typedef struct {
    int x;
    int y;
} Point;

typedef enum {
    RED,
    GREEN,
    BLUE
} Color;

#define MAX_SIZE 100
#define DEBUG_MODE 1

extern int global_config_value;

void utility_function();
int helper_function(int param);

#endif // UTILS_H