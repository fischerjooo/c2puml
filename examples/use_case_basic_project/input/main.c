#include <stdio.h>
#include "utils.h"
#include "types.h"

int global_counter = 0;
char* global_name = "Basic Project";

int add(int a, int b) {
    return a + b;
}

float multiply(float x, float y) {
    return x * y;
}

void print_point(Point p) {
    printf("Point: (%d, %d)\n", p.x, p.y);
}

int main() {
    Point p = {10, 20};
    Rectangle rect = {{0, 0}, {100, 100}, RED};
    
    print_point(p);
    printf("Area: %f\n", multiply(rect.bottom_right.x - rect.top_left.x, 
                                  rect.bottom_right.y - rect.top_left.y));
    
    return 0;
}