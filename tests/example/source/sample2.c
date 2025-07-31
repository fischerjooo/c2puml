#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "sample.h"
#include "math_utils.h"
#include "logger.h"
#include "geometry.h"
#include "filtered_header.h"
#include "first_level.h"

#define MAX_SIZE 100U
#define DEBUG_MODE 1U
#define CALC(x, y) ((x) + (y))

/* Global variables */
static int global_counter = 0;
static char buffer[MAX_SIZE];
double *global_ptr = NULL;

/* Function prototypes */
static void internal_helper(void);
int calculate_sum(int a, int b);
point_t *create_point(int x, int y, const char *label);

/* Static function implementation */
static void internal_helper(void)
{
    printf("Internal helper called\n");
    global_counter++;
}

/* Public function implementations */
int calculate_sum(int a, int b)
{
    return CALC(a, b);
}

point_t *create_point(int x, int y, const char *label)
{
    point_t *p = (point_t *)malloc(sizeof(point_t));
    if (p != NULL)
    {
        p->x = x;
        p->y = y;
        (void)strncpy(p->label, label, (sizeof(p->label) - 1U));
        p->label[sizeof(p->label) - 1U] = '\0';
    }
    return p;
}

void process_point(point_t *p)
{
    if (p == NULL)
    {
        return;
    }
    printf("Point: (%d, %d) - %s\n", p->x, p->y, p->label);
    internal_helper();
}

/* Add a function that uses triangle_t and logging */
void demo_triangle_usage(void)
{
    point_t a = {0, 0, "A"};
    point_t b = {4, 0, "B"};
    point_t c = {0, 3, "C"};
    triangle_t tri = create_triangle(&a, &b, &c, "DemoTriangle");
    int area = triangle_area(&tri);
    log_message(LOG_INFO, "Triangle '%s' area: %d", tri.label, area);
}

int main(void)
{
    point_t *p1 = create_point(10, 20, "First Point");
    point_t *p2 = create_point(30, 40, "Second Point");

    process_point(p1);
    process_point(p2);

    printf("Total operations: %d\n", global_counter);

    free(p1);
    free(p2);

    demo_triangle_usage();

    return 0;
}
