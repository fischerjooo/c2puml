#ifndef SAMPLE_H
#define SAMPLE_H

#include <stddef.h>
#include "config.h"

#define PI 3.14159
#define VERSION "1.0.0"

/* Full definition of point_t struct */
typedef struct point_tag {
    int x;
    int y;
    char label[32];
} point_t;

/* Full definition of system_state_t enum */
typedef enum system_state_tag {
    STATE_IDLE = 0,
    STATE_RUNNING,
    STATE_ERROR
} system_state_t;

/* Function prototypes */
extern int calculate_sum(int a, int b);
extern point_t * create_point(int x, int y, const char * label);
extern void process_point(point_t * p);

#include "geometry.h"
#include "logger.h"

#define MIN(a, b) ((a) < (b) ? (a) : (b))
#define MAX(a, b) ((a) > (b) ? (a) : (b))

extern const int MAX_POINTS;
extern const char * DEFAULT_LABEL;

#endif /* SAMPLE_H */