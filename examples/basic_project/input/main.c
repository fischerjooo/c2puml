#include <stdio.h>
#include <stdlib.h>
#include "utils.h"
#include "types.h"

// Global variables
int global_counter = 0;
String global_name = "Basic Project";

// Function implementations
int add(int a, int b) {
    return a + b;
}

float multiply(float x, float y) {
    return x * y;
}

void print_point(Point p) {
    printf("Point: (%d, %d)\n", p.x, p.y);
}

Color get_color(int index) {
    switch (index) {
        case 0: return RED;
        case 1: return GREEN;
        case 2: return BLUE;
        default: return RED;
    }
}

Value create_value(int type, void* data) {
    Value v;
    switch (type) {
        case 0:
            v.i = *(int*)data;
            break;
        case 1:
            v.f = *(float*)data;
            break;
        case 2:
            v.c = *(char*)data;
            break;
    }
    return v;
}

int main() {
    Point p = {10, 20};
    Rectangle rect = {{0, 0}, {100, 100}, RED};
    Circle circle = {{50, 50}, 25.5, BLUE};
    
    print_point(p);
    printf("Area: %f\n", multiply(rect.bottom_right.x - rect.top_left.x, 
                                  rect.bottom_right.y - rect.top_left.y));
    
    return 0;
}