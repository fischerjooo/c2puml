#include "geometry.h"
#include <string.h>

triangle_t create_triangle(const point_t* a, const point_t* b, const point_t* c, const char* label) {
    triangle_t tri;
    tri.vertices[0] = *a;
    tri.vertices[1] = *b;
    tri.vertices[2] = *c;
    strncpy(tri.label, label, MAX_LABEL_LEN-1);
    tri.label[MAX_LABEL_LEN-1] = '\0';
    return tri;
}

// Simple area calculation (not accurate, just for demo)
int triangle_area(const triangle_t* tri) {
    int x1 = tri->vertices[0].x, y1 = tri->vertices[0].y;
    int x2 = tri->vertices[1].x, y2 = tri->vertices[1].y;
    int x3 = tri->vertices[2].x, y3 = tri->vertices[2].y;
    return abs((x1*(y2-y3) + x2*(y3-y1) + x3*(y1-y2))/2);
}