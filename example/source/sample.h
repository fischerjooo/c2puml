#ifndef SAMPLE_H
#define SAMPLE_H

#include <stddef.h>
#include "config.h"

#define PI 3.14159
#define VERSION "1.0.0"

/* Forward declarations with explicit tags */
typedef struct point_tag point_t;
typedef enum system_state_tag system_state_t;

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