#ifndef SAMPLE_H
#define SAMPLE_H

#include <stddef.h>

#define PI 3.14159
#define VERSION "1.0.0"

// Forward declarations
typedef struct point point_t;
typedef enum system_state system_state_t;

// Function prototypes
extern int calculate_sum(int a, int b);
extern point_t* create_point(int x, int y, const char* label);
extern void process_point(point_t* p);

// Utility macros
#define MIN(a, b) ((a) < (b) ? (a) : (b))
#define MAX(a, b) ((a) > (b) ? (a) : (b))

// Constants
extern const int MAX_POINTS;
extern const char* DEFAULT_LABEL;

#endif // SAMPLE_H