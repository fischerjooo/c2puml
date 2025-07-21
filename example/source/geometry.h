#ifndef GEOMETRY_H
#define GEOMETRY_H

#include "sample.h"
#include "math_utils.h"

// New struct using point_t
typedef struct {
    point_t vertices[3];
    char label[MAX_LABEL_LEN];
} triangle_t;

// Function prototypes
triangle_t create_triangle(const point_t* a, const point_t* b, const point_t* c, const char* label);
int triangle_area(const triangle_t* tri);

#endif // GEOMETRY_H