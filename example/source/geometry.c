#include "geometry.h"
#include <string.h>
#include <stdlib.h>

triangle_t create_triangle(const point_t * a, const point_t * b, const point_t * c, const char * label)
{
    triangle_t tri;
    tri.vertices[0] = *a;
    tri.vertices[1] = *b;
    tri.vertices[2] = *c;
    (void)strncpy(tri.label, label, (size_t)(MAX_LABEL_LEN - 1U));
    tri.label[MAX_LABEL_LEN - 1U] = '\0';
    return tri;
}

/* Simple area calculation (not accurate, just for demo) */
int triangle_area(const triangle_t * tri)
{
    int x1 = tri->vertices[0].x;
    int y1 = tri->vertices[0].y;
    int x2 = tri->vertices[1].x;
    int y2 = tri->vertices[1].y;
    int x3 = tri->vertices[2].x;
    int y3 = tri->vertices[2].y;
    int area = abs((x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2)) / 2);
    return area;
}